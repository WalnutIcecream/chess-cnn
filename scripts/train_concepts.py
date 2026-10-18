#!/usr/bin/env python3
"""Train the concept classifier on the Lichess puzzle tags.

This is the first model in the project trained on **independent** ground truth: the targets
are Lichess's curated tactic tags, not this project's rule labels. The theme head of
:class:`~moveexp.model.network.MoveNet` predicts the ``THEME_VOCAB`` multi-hot vector from the
board (and, by default, the played move), so the numbers here answer the question the earlier
self-play baseline could not: "can a network learn real chess concepts from the board alone?"

The decision threshold is tuned on the validation split (one global threshold, or a per-tag
threshold) rather than fixed at 0.5, because the tactic tags are heavily imbalanced and 0.5 is
almost never the macro-F1 optimum.

Run inside the venv (torch extra required)::

    python scripts/build_puzzle_dataset.py --n 200000
    python scripts/train_concepts.py --labels data/processed/puzzles.parquet
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np

from moveexp.config import DEFAULT_SEED, PROJECT_ROOT, SPLIT_FRACTIONS, THEME_VOCAB
from moveexp.model import build_puzzle_dataset, group_split
from moveexp.model.metrics import multilabel_macro_f1, multilabel_micro_f1
from moveexp.model.network import MoveNet

RESULTS_CSV = PROJECT_ROOT / "experiments" / "concepts_vs_tags.csv"


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


def _prevalence_baseline(train_targets: np.ndarray, n_rows: int) -> np.ndarray:
    """The trivial per-tag majority predictor: a tag is predicted on every row if it is common."""
    prevalence = train_targets.mean(axis=0) > 0.5
    return np.repeat(prevalence.astype(np.float32)[None, :], n_rows, axis=0)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--labels", type=Path, required=True, help="Puzzle-concept Parquet.")
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--channels", type=int, default=32)
    parser.add_argument("--hidden", type=int, default=128)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--no-move", action="store_true", help="Ablation: drop move planes.")
    parser.add_argument("--race", type=int, default=12, help="Max pos_weight (class balancing).")
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

    best_val_f1, best_state = -1.0, {k: v.clone() for k, v in model.state_dict().items()}
    for epoch in range(args.epochs):
        model.train()
        order = torch.randperm(len(train))
        total, batches = 0.0, 0
        for start in range(0, len(order), args.batch_size):
            batch = order[start : start + args.batch_size]
            optimiser.zero_grad()
            _, theme_logits, _ = model(x_train[batch])
            loss = bce(theme_logits, y_train[batch])
            loss.backward()
            optimiser.step()
            total += float(loss.detach())
            batches += 1
        model.eval()
        with torch.no_grad():
            _, val_logits, _ = model(x_val)
            val_probs = torch.sigmoid(val_logits).numpy()
        _t, val_f1 = tune_global_threshold(val_probs, y_val_np)
        print(
            f"  epoch {epoch + 1:>2}/{args.epochs}  loss={total / max(batches, 1):.4f}  val_macro_f1={val_f1:.3f}"
        )
        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
    model.load_state_dict(best_state)

    model.eval()
    with torch.no_grad():
        _, test_logits, _ = model(x_test)
        test_probs = torch.sigmoid(test_logits).numpy()
        _, val_logits, _ = model(x_val)
        val_probs = torch.sigmoid(val_logits).numpy()

    threshold, _ = tune_global_threshold(val_probs, y_val_np)
    test_pred = (test_probs >= threshold).astype(np.float32)

    variant = "without_move" if args.no_move else "with_move"
    micro = multilabel_micro_f1(y_test_np, test_pred)
    macro = multilabel_macro_f1(y_test_np, test_pred)
    all_off = np.zeros_like(test_pred)
    baseline = _prevalence_baseline(y_themes[train], len(test))

    print(
        f"[{variant}] planes={x.shape[1]} rows={len(x)} "
        f"train/val/test={len(train)}/{len(val)}/{len(test)} "
        f"threshold={threshold:.2f}"
    )
    for name, pred in (("model", test_pred), ("all-off", all_off), ("prevalence", baseline)):
        print(
            f"  {name:<11} micro_f1={multilabel_micro_f1(y_test_np, pred):.3f}  "
            f"macro_f1={multilabel_macro_f1(y_test_np, pred):.3f}"
        )

    scores = per_tag_prf(y_test_np, test_pred)
    ranked = sorted(
        ((THEME_VOCAB[i], s) for i, s in enumerate(scores) if s is not None),
        key=lambda item: item[1][2],
        reverse=True,
    )
    print("  per-tag F1 (held-out puzzles):")
    for name, (precision, recall, f1) in ranked:
        print(f"    {name:<22} P={precision:.3f} R={recall:.3f} F1={f1:.3f}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    header = ["variant", "head", "metric", "model", "all_off", "prevalence_baseline"]
    with args.out.open(
        "w" if args.overwrite or not args.out.exists() else "a", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.writer(handle)
        if args.overwrite or not args.out.exists():
            writer.writerow(header)
        writer.writerow(
            [
                variant,
                "theme",
                "micro_f1",
                f"{micro:.4f}",
                f"{multilabel_micro_f1(y_test_np, all_off):.4f}",
                f"{multilabel_micro_f1(y_test_np, baseline):.4f}",
            ]
        )
        writer.writerow(
            [
                variant,
                "theme",
                "macro_f1",
                f"{macro:.4f}",
                f"{multilabel_macro_f1(y_test_np, all_off):.4f}",
                f"{multilabel_macro_f1(y_test_np, baseline):.4f}",
            ]
        )
    print(f"appended results to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
