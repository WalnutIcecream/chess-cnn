#!/usr/bin/env python3
"""Train the concept classifier on the Lichess puzzle tags.

This is the first model in the project trained on **independent** ground truth: the targets
are Lichess's curated tactic tags, not this project's rule labels. The theme head of
:class:`~moveexp.model.network.MoveNet` predicts the ``THEME_VOCAB`` multi-hot vector from the
board (and, by default, the played move), so the numbers here answer the question the earlier
self-play baseline could not: "can a network learn real chess concepts from the board alone?"

Decision thresholds are tuned on the validation split, **one per tag**, and the model is
reported both that way and under a single global threshold for comparison. One global value is
what previously left eight rare tags at F1 0.00: the threshold that maximises macro F1 overall
sits far above any probability the model emits for a rare motif, so those tags were never
predicted at all.

The bar it is measured against is a **top-k prevalence baseline** (predict the ``k`` most
common training tags on every row, ``k`` tuned on validation). The per-tag majority predictor
used earlier is not a bar at all here -- no tag appears in more than half the rows, so it
degenerates to all-off and scores 0.000.

Training supports symmetry augmentation (mirror and colour flip, per sample) and a cosine
learning-rate schedule, but on this dataset **neither helped**: at ten epochs each scored below
plain training (macro F1 0.343 and 0.289 against 0.370), so both are off by default and kept as
flags for the ablation (``--augment``, ``--schedule cosine``). Early stopping stays on
(``--patience``). See PROGRESS §22 for the table and the caveats.

Run inside the venv (torch extra required)::

    python scripts/build_puzzle_dataset.py --n 200000
    python scripts/train_concepts.py --labels data/processed/puzzles.parquet
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from moveexp.config import DEFAULT_SEED, PROJECT_ROOT, SPLIT_FRACTIONS, THEME_VOCAB
from moveexp.model import build_puzzle_dataset, group_split
from moveexp.model.encode import N_PIECES
from moveexp.model.metrics import binary_f1, multilabel_macro_f1, multilabel_micro_f1
from moveexp.model.network import MoveNet

if TYPE_CHECKING:  # pragma: no cover - the augmentation helpers are typed, not imported
    import torch

RESULTS_CSV = PROJECT_ROOT / "experiments" / "concepts_vs_tags.csv"
ABLATION_CSV = PROJECT_ROOT / "experiments" / "concepts_ablation.csv"


def _binary_prf(true_col: np.ndarray, pred_col: np.ndarray) -> tuple[float, float, float] | None:
    """Precision, recall and F1 of one binary column (``None`` when it never occurs)."""
    tp = int((true_col * pred_col).sum())
    fp = int(((1 - true_col) * pred_col).sum())
    fn = int((true_col * (1 - pred_col)).sum())
    if tp + fp + fn == 0:
        return None
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def per_tag_prf(y_true: np.ndarray, y_pred: np.ndarray) -> list[tuple[float, float, float] | None]:
    """Per-column precision/recall/F1 for a binary multi-label array."""
    return [_binary_prf(y_true[:, c], y_pred[:, c]) for c in range(y_true.shape[1])]


def tune_global_threshold(
    probs: np.ndarray, y_true: np.ndarray, *, lo: float = 0.05, hi: float = 0.95, step: float = 0.05
) -> tuple[float, float]:
    """Pick the single threshold maximising macro F1 on ``(probs, y_true)``.

    :returns: ``(threshold, macro_f1_at_that_threshold)``.
    """
    best_t, best_f1 = 0.5, -1.0
    for t in np.arange(lo, hi + 1e-9, step):
        f1 = multilabel_macro_f1(y_true, (probs >= t).astype(np.float32))
        if f1 > best_f1:
            best_t, best_f1 = float(t), f1
    return best_t, best_f1


def tune_per_tag_thresholds(
    probs: np.ndarray,
    y_true: np.ndarray,
    *,
    lo: float = 0.05,
    hi: float = 0.95,
    step: float = 0.05,
) -> np.ndarray:
    """One threshold per tag, each maximising *that* tag's F1 on ``(probs, y_true)``.

    A single global threshold is what left eight rare tags at F1 0.00: the value that maximises
    macro F1 *overall* sits far above the probability the model ever emits for a rare motif, so
    those tags were never predicted at all. Tuning each column separately removes that coupling.
    A tag with no positive in the tuning set keeps the neutral ``0.5`` rather than being tuned
    against an empty column (which would drive its threshold to the bottom of the grid).
    """
    thresholds = np.full(probs.shape[1], 0.5, dtype=np.float32)
    grid = np.arange(lo, hi + 1e-9, step)
    for column in range(probs.shape[1]):
        truth = y_true[:, column]
        if truth.sum() == 0:
            continue
        best_t, best_f1 = 0.5, -1.0
        for t in grid:
            f1 = binary_f1(truth, (probs[:, column] >= t).astype(np.float32))
            if f1 > best_f1:
                best_t, best_f1 = float(t), f1
        thresholds[column] = best_t
    return thresholds


def apply_per_tag_thresholds(probs: np.ndarray, thresholds: np.ndarray) -> np.ndarray:
    """Threshold every column by its own value."""
    return (probs >= thresholds[None, :]).astype(np.float32)


def top_k_baseline(train_targets: np.ndarray, n_rows: int, k: int) -> np.ndarray:
    """The ``k`` most common training tags, predicted on every row.

    The majority predictor degenerates to all-off on this data (no tag appears in more than half
    the rows), so it scores 0.000 and proves nothing. This one always answers, which makes it a
    bar the model has to clear.
    """
    prevalence = train_targets.mean(axis=0)
    top = np.argsort(prevalence)[::-1][: max(0, k)]
    out = np.zeros((n_rows, train_targets.shape[1]), dtype=np.float32)
    out[:, top] = 1.0
    return out


def tune_top_k(
    train_targets: np.ndarray, y_val: np.ndarray, *, max_k: int = 12
) -> tuple[int, float]:
    """Choose ``k`` to maximise the top-k baseline's **micro** F1 on the validation set.

    Micro is the right criterion: macro would keep rewarding a larger ``k`` (a tag predicted
    everywhere gets F1 = 2p/(1+p), which rises with its prevalence), so macro would simply pick
    the largest ``k`` and call that a baseline.
    """
    best_k, best_f1 = 1, -1.0
    for k in range(1, max_k + 1):
        f1 = multilabel_micro_f1(y_val, top_k_baseline(train_targets, len(y_val), k))
        if f1 > best_f1:
            best_k, best_f1 = k, f1
    return best_k, best_f1


# --------------------------------------------------------------------------------------
# Training improvements: symmetry augmentation and a learning-rate schedule
# --------------------------------------------------------------------------------------


def transform_batch(x: torch.Tensor, *, mirror: bool, switch_colour: bool) -> torch.Tensor:
    """Apply the requested board symmetries to a batch of encoded positions.

    The torch twin of :func:`moveexp.model.encode.augment_planes`, kept here so the training
    loop never leaves the tensor world; a test pins the two together so they cannot drift.
    """
    out = x
    if switch_colour:
        half = N_PIECES // 2
        swapped = x.new_empty(x.shape)
        swapped[:, :half] = x[:, half:N_PIECES].flip(-2, -1)
        swapped[:, half:N_PIECES] = x[:, :half].flip(-2, -1)
        swapped[:, N_PIECES] = 1.0 - x[:, N_PIECES]
        swapped[:, N_PIECES + 1 :] = x[:, N_PIECES + 1 :].flip(-2, -1)
        out = swapped
    if mirror:
        out = out.flip(-1)
    return out


def augment_batch(x: torch.Tensor, rng: np.random.Generator) -> torch.Tensor:
    """Mirror and/or colour-flip each sample independently.

    Both are board symmetries -- the mover's win probability and every theme label are
    unchanged -- so this is free training data. It is applied over the four (mirror, colour)
    combinations rather than per sample so it stays vectorised.
    """
    mirror = rng.integers(0, 2, size=x.shape[0]).astype(bool)
    switch = rng.integers(0, 2, size=x.shape[0]).astype(bool)
    out = x.clone()
    for want_mirror in (False, True):
        for want_switch in (False, True):
            selected = (mirror == want_mirror) & (switch == want_switch)
            if not selected.any():
                continue
            out[selected] = transform_batch(
                x[selected], mirror=want_mirror, switch_colour=want_switch
            )
    return out


def cosine_lr(base_lr: float, epoch: int, total_epochs: int, *, min_ratio: float = 0.05) -> float:
    """Cosine decay from ``base_lr`` to ``min_ratio * base_lr`` across ``total_epochs``.

    Written out rather than delegated to a ``torch`` scheduler so the shape is testable: it
    starts at ``base_lr``, ends at the floor, and never increases.
    """
    if total_epochs <= 1:
        return base_lr
    progress = min(1.0, max(0.0, epoch / (total_epochs - 1)))
    factor = min_ratio + (1.0 - min_ratio) * 0.5 * (1.0 + math.cos(math.pi * progress))
    return base_lr * factor


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--labels", type=Path, required=True, help="Puzzle-concept Parquet.")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--channels", type=int, default=32)
    parser.add_argument("--hidden", type=int, default=128)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--no-move", action="store_true", help="Ablation: drop move planes.")
    parser.add_argument("--race", type=int, default=12, help="Max pos_weight (class balancing).")
    parser.add_argument(
        "--augment",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Mirror / colour-flip each training batch. Both are label-preserving symmetries, "
        "but this measured worse than plain training here, so it is off by default.",
    )
    parser.add_argument(
        "--schedule",
        choices=("none", "cosine"),
        default="none",
        help="Learning-rate schedule. 'none' measured best here; 'cosine' is kept for the "
        "ablation.",
    )
    parser.add_argument(
        "--patience",
        type=int,
        default=3,
        help="Stop after this many epochs without a validation improvement (0 = never).",
    )
    parser.add_argument("--out", type=Path, default=RESULTS_CSV)
    parser.add_argument("--overwrite", action="store_true", help="Truncate the results CSV.")
    args = parser.parse_args(argv)

    import pandas as pd
    import torch
    from torch import nn

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    frame = pd.read_parquet(args.labels)
    rows = frame.to_dict("records")
    x, y_themes, puzzle_ids = build_puzzle_dataset(rows, use_move=not args.no_move)
    split = group_split(puzzle_ids, seed=args.seed, fractions=SPLIT_FRACTIONS)
    train, val, test = split["train"], split["val"], split["test"]
    if len(test) == 0 or len(val) == 0:
        raise SystemExit("need at least three puzzles to hold out a validation and test split")

    x_train = torch.from_numpy(x[train])
    y_train = torch.from_numpy(y_themes[train])
    x_val = torch.from_numpy(x[val])
    y_val_np = y_themes[val]
    x_test = torch.from_numpy(x[test])
    y_test_np = y_themes[test]

    frequency = y_themes[train].mean(axis=0)
    pos_weight = torch.tensor(
        np.clip((1.0 - frequency) / np.maximum(frequency, 1e-3), 1.0, float(args.race)),
        dtype=torch.float32,
    )
    bce = nn.BCEWithLogitsLoss(pos_weight=pos_weight)

    model = MoveNet(x.shape[1], channels=args.channels, hidden=args.hidden)
    optimiser = torch.optim.Adam(model.parameters(), lr=args.lr)
    augment_rng = np.random.default_rng(args.seed)

    best_val_f1, best_state = -1.0, {k: v.clone() for k, v in model.state_dict().items()}
    stale = 0
    for epoch in range(args.epochs):
        if args.schedule == "cosine":
            lr = cosine_lr(args.lr, epoch, args.epochs)
            for group in optimiser.param_groups:
                group["lr"] = lr
        model.train()
        order = torch.randperm(len(train))
        total, batches = 0.0, 0
        for start in range(0, len(order), args.batch_size):
            batch = order[start : start + args.batch_size]
            batch_x = x_train[batch]
            if args.augment:
                batch_x = augment_batch(batch_x, augment_rng)
            optimiser.zero_grad()
            _, theme_logits, _ = model(batch_x)
            loss = bce(theme_logits, y_train[batch])
            loss.backward()
            optimiser.step()
            total += float(loss.detach())
            batches += 1
        model.eval()
        with torch.no_grad():
            _, val_logits, _ = model(x_val)
            val_probs = torch.sigmoid(val_logits).numpy()
        # Early stopping tracks the metric we actually report (macro F1 under per-tag
        # thresholds), not macro F1 under a single global threshold, which flatters the model
        # by ignoring exactly the rare tags we are trying to fix.
        val_thresholds = tune_per_tag_thresholds(val_probs, y_val_np)
        val_f1 = multilabel_macro_f1(y_val_np, apply_per_tag_thresholds(val_probs, val_thresholds))
        current_lr = optimiser.param_groups[0]["lr"]
        print(
            f"  epoch {epoch + 1:>2}/{args.epochs}  lr={current_lr:.2e}  "
            f"loss={total / max(batches, 1):.4f}  val_macro_f1={val_f1:.3f}"
        )
        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
            stale = 0
        else:
            stale += 1
            if args.patience and stale >= args.patience:
                print(f"  early stop: no validation improvement for {args.patience} epoch(s)")
                break
    model.load_state_dict(best_state)

    model.eval()
    with torch.no_grad():
        _, test_logits, _ = model(x_test)
        test_probs = torch.sigmoid(test_logits).numpy()
        _, val_logits, _ = model(x_val)
        val_probs = torch.sigmoid(val_logits).numpy()

    global_threshold, _ = tune_global_threshold(val_probs, y_val_np)
    per_tag = tune_per_tag_thresholds(val_probs, y_val_np)
    test_global = (test_probs >= global_threshold).astype(np.float32)
    test_per_tag = apply_per_tag_thresholds(test_probs, per_tag)
    all_off = np.zeros_like(test_per_tag)

    baseline_k, baseline_micro = tune_top_k(y_themes[train], y_val_np)
    baseline = top_k_baseline(y_themes[train], len(test), baseline_k)

    variant = "without_move" if args.no_move else "with_move"
    print(
        f"[{variant}] planes={x.shape[1]} rows={len(x)} augment={args.augment} "
        f"schedule={args.schedule} train/val/test={len(train)}/{len(val)}/{len(test)}"
    )
    print(f"  global threshold={global_threshold:.2f}; per-tag thresholds on val")
    print(f"  top-k baseline: k={baseline_k} (chosen by val micro F1={baseline_micro:.3f})")
    predictions = (
        ("model(global)", test_global),
        ("model(per-tag)", test_per_tag),
        ("all-off", all_off),
        (f"top-{baseline_k}", baseline),
    )
    for name, pred in predictions:
        print(
            f"  {name:<15} micro_f1={multilabel_micro_f1(y_test_np, pred):.3f}  "
            f"macro_f1={multilabel_macro_f1(y_test_np, pred):.3f}"
        )

    def _scored(scores: list[tuple[float, float, float] | None]) -> int:
        return sum(1 for score in scores if score is not None)

    global_scores = per_tag_prf(y_test_np, test_global)
    tag_scores = per_tag_prf(y_test_np, test_per_tag)
    print(
        f"  tags scored at all: global={_scored(global_scores)} "
        f"per-tag={_scored(tag_scores)} of {len(THEME_VOCAB)}"
    )

    ranked = sorted(
        ((THEME_VOCAB[i], s) for i, s in enumerate(tag_scores) if s is not None),
        key=lambda item: item[1][2],
        reverse=True,
    )
    print("  per-tag F1 under per-tag thresholds (held-out puzzles):")
    for name, (precision, recall, f1) in ranked:
        print(f"    {name:<22} P={precision:.3f} R={recall:.3f} F1={f1:.3f}")

    micro_global = multilabel_micro_f1(y_test_np, test_global)
    macro_global = multilabel_macro_f1(y_test_np, test_global)
    micro_per_tag = multilabel_micro_f1(y_test_np, test_per_tag)
    macro_per_tag = multilabel_macro_f1(y_test_np, test_per_tag)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    header = [
        "variant",
        "augment",
        "schedule",
        "head",
        "metric",
        "model_global",
        "model_per_tag",
        "all_off",
        "topk_baseline",
        "topk_k",
    ]
    fields = {
        "micro_f1": (micro_global, micro_per_tag, multilabel_micro_f1(y_test_np, baseline)),
        "macro_f1": (macro_global, macro_per_tag, multilabel_macro_f1(y_test_np, baseline)),
    }
    new_file = args.overwrite or not args.out.exists()
    with args.out.open("w" if new_file else "a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        if new_file:
            writer.writerow(header)
        for metric, (global_score, per_tag_score, topk_score) in fields.items():
            writer.writerow(
                [
                    variant,
                    int(args.augment),
                    args.schedule,
                    "theme",
                    metric,
                    f"{global_score:.4f}",
                    f"{per_tag_score:.4f}",
                    "0.0000",
                    f"{topk_score:.4f}",
                    baseline_k,
                ]
            )
    print(f"appended results to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
