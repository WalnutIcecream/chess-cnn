#!/usr/bin/env python3
"""Train the tiny CNN on the rule-generated labels and compare it to trivial baselines.

The labels are produced by the symbolic layer, so this measures *learnability* (can a
network recover the rule labels from the board alone?) rather than correctness against
ground truth. Two variants are supported for the ablation the brief asks for: with the
played move encoded as input planes, and without it.

Run inside the venv (torch extra required)::

    .venv\\Scripts\\python.exe scripts/train_model.py --labels data/processed/selfplay.parquet
    .venv\\Scripts\\python.exe scripts/train_model.py --labels ... --no-move
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np

from moveexp.config import PROJECT_ROOT, QUALITY_LABELS, SPLIT_FRACTIONS
from moveexp.model import build_dataset, build_intent_targets, group_split
from moveexp.model.network import MoveNet

RESULTS_CSV = PROJECT_ROOT / "experiments" / "model_vs_rules.csv"


# --------------------------------------------------------------------------------------
# Metrics (hand-rolled: sklearn is not a dependency)
# --------------------------------------------------------------------------------------


def accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float((y_true == y_pred).mean()) if len(y_true) else 0.0


def macro_f1(y_true: np.ndarray, y_pred: np.ndarray, n_classes: int) -> float:
    """Macro F1 over classes present in the union of truth and predictions."""
    scores: list[float] = []
    for cls in range(n_classes):
        tp = int(((y_pred == cls) & (y_true == cls)).sum())
        fp = int(((y_pred == cls) & (y_true != cls)).sum())
        fn = int(((y_pred != cls) & (y_true == cls)).sum())
        if tp + fp + fn == 0:
            continue
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        scores.append(2 * precision * recall / (precision + recall) if precision + recall else 0.0)
    return float(np.mean(scores)) if scores else 0.0


def _binary_f1(true_col: np.ndarray, pred_col: np.ndarray) -> float | None:
    tp = int((true_col * pred_col).sum())
    fp = int(((1 - true_col) * pred_col).sum())
    fn = int((true_col * (1 - pred_col)).sum())
    if tp + fp + fn == 0:
        return None
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def multilabel_micro_f1(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    tp = int((y_true * y_pred).sum())
    fp = int(((1 - y_true) * y_pred).sum())
    fn = int((y_true * (1 - y_pred)).sum())
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def multilabel_macro_f1(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    scores = [
        score
        for col in range(y_true.shape[1])
        if (score := _binary_f1(y_true[:, col], y_pred[:, col])) is not None
    ]
    return float(np.mean(scores)) if scores else 0.0


# --------------------------------------------------------------------------------------
# Training / evaluation
# --------------------------------------------------------------------------------------


def _train(args: argparse.Namespace, use_move: bool) -> list[dict[str, object]]:
    import pandas as pd
    import torch
    from torch import nn

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    frame = pd.read_parquet(args.labels)
    rows = frame.to_dict("records")
    x, y_quality, y_themes, game_ids = build_dataset(rows, use_move=use_move)
    y_intents = build_intent_targets(rows)
    split = group_split(game_ids, seed=args.seed, fractions=SPLIT_FRACTIONS)
    train, val, test = split["train"], split["val"], split["test"]
    if len(test) == 0:
        raise SystemExit("held-out split is empty; generate more games")

    def tensor(indices: np.ndarray) -> tuple:
        return (
            torch.from_numpy(x[indices]),
            torch.from_numpy(y_quality[indices]),
            torch.from_numpy(y_themes[indices]),
            torch.from_numpy(y_intents[indices]),
        )

    x_train, yq_train, yt_train, yi_train = tensor(train)
    x_val, yq_val, yt_val, yi_val = tensor(val)
    x_test, yq_test, yt_test, yi_test = tensor(test)

    model = MoveNet(x.shape[1], channels=args.channels, hidden=args.hidden)
    optimiser = torch.optim.Adam(model.parameters(), lr=args.lr)

    # Labels are heavily imbalanced (most moves are "best"; a few themes dominate), so the
    # losses are weighted to stop the constant predictor from being a local optimum.
    quality_counts = np.bincount(y_quality[train], minlength=len(QUALITY_LABELS)).astype(np.float32)
    quality_weights = quality_counts.sum() / np.maximum(quality_counts, 1.0)
    quality_weights = quality_weights / quality_weights.mean()
    cross_entropy = nn.CrossEntropyLoss(weight=torch.tensor(quality_weights, dtype=torch.float32))
    theme_frequency = y_themes[train].mean(axis=0)
    pos_weight = torch.tensor(
        np.clip((1.0 - theme_frequency) / np.maximum(theme_frequency, 1e-3), 1.0, 20.0),
        dtype=torch.float32,
    )
    bce = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    intent_frequency = y_intents[train].mean(axis=0)
    intent_pos_weight = torch.tensor(
        np.clip((1.0 - intent_frequency) / np.maximum(intent_frequency, 1e-3), 1.0, 20.0),
        dtype=torch.float32,
    )
    intent_bce = nn.BCEWithLogitsLoss(pos_weight=intent_pos_weight)

    best_val = float("inf")
    best_state = {k: v.clone() for k, v in model.state_dict().items()}
    for _epoch in range(args.epochs):
        model.train()
        order = torch.randperm(len(train))
        for start in range(0, len(order), args.batch_size):
            batch = order[start : start + args.batch_size]
            optimiser.zero_grad()
            q_logits, t_logits, i_logits = model(x_train[batch])
            loss = (
                cross_entropy(q_logits, yq_train[batch])
                + bce(t_logits, yt_train[batch])
                + intent_bce(i_logits, yi_train[batch])
            )
            loss.backward()
            optimiser.step()
        model.eval()
        with torch.no_grad():
            q_logits, t_logits, i_logits = model(x_val)
            val_loss = float(
                cross_entropy(q_logits, yq_val)
                + bce(t_logits, yt_val)
                + intent_bce(i_logits, yi_val)
            )
        if val_loss < best_val:
            best_val = val_loss
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
    model.load_state_dict(best_state)

    model.eval()
    with torch.no_grad():
        q_logits, t_logits, i_logits = model(x_test)
        q_pred = q_logits.argmax(dim=1).numpy()
        t_pred = (torch.sigmoid(t_logits) >= 0.5).float().numpy()
        i_pred = (torch.sigmoid(i_logits) >= 0.5).float().numpy()
        train_q = model(x_train)[0].argmax(dim=1).numpy()

    yq_test_np = yq_test.numpy()
    yt_test_np = yt_test.numpy()
    yi_test_np = yi_test.numpy()

    # Baselines: majority quality class, and per-theme majority (always-on if common).
    q_majority = int(np.bincount(y_quality[train]).argmax())
    q_baseline = np.full_like(yq_test_np, q_majority)
    theme_prevalence = y_themes[train].mean(axis=0)
    t_baseline = np.repeat((theme_prevalence > 0.5).astype(np.float32)[None, :], len(test), axis=0)
    intent_prevalence = y_intents[train].mean(axis=0)
    i_baseline = np.repeat((intent_prevalence > 0.5).astype(np.float32)[None, :], len(test), axis=0)

    variant = "with_move" if use_move else "without_move"
    rows_out: list[dict[str, object]] = [
        {
            "variant": variant,
            "head": "quality",
            "metric": "accuracy",
            "model": accuracy(yq_test_np, q_pred),
            "majority_baseline": accuracy(yq_test_np, q_baseline),
        },
        {
            "variant": variant,
            "head": "quality",
            "metric": "macro_f1",
            "model": macro_f1(yq_test_np, q_pred, len(QUALITY_LABELS)),
            "majority_baseline": macro_f1(yq_test_np, q_baseline, len(QUALITY_LABELS)),
        },
        {
            "variant": variant,
            "head": "theme",
            "metric": "micro_f1",
            "model": multilabel_micro_f1(yt_test_np, t_pred),
            "majority_baseline": multilabel_micro_f1(yt_test_np, t_baseline),
        },
        {
            "variant": variant,
            "head": "theme",
            "metric": "macro_f1",
            "model": multilabel_macro_f1(yt_test_np, t_pred),
            "majority_baseline": multilabel_macro_f1(yt_test_np, t_baseline),
        },
        {
            "variant": variant,
            "head": "intent",
            "metric": "micro_f1",
            "model": multilabel_micro_f1(yi_test_np, i_pred),
            "majority_baseline": multilabel_micro_f1(yi_test_np, i_baseline),
        },
        {
            "variant": variant,
            "head": "intent",
            "metric": "macro_f1",
            "model": multilabel_macro_f1(yi_test_np, i_pred),
            "majority_baseline": multilabel_macro_f1(yi_test_np, i_baseline),
        },
    ]

    print(
        f"[{variant}] planes={x.shape[1]} rows={len(x)} "
        f"train/val/test={len(train)}/{len(val)}/{len(test)} "
        f"best_val_loss={best_val:.4f} majority_quality={QUALITY_LABELS[q_majority]} "
        f"train_acc={accuracy(yq_train.numpy(), train_q):.3f}"
    )
    for row in rows_out:
        print(
            f"  {row['head']:<7} {row['metric']:<9} model={row['model']:.3f} "
            f"majority_baseline={row['majority_baseline']:.3f}"
        )
    return rows_out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels", type=Path, required=True, help="Labelled Parquet file.")
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--channels", type=int, default=32)
    parser.add_argument("--hidden", type=int, default=128)
    parser.add_argument("--seed", type=int, default=20240917)
    parser.add_argument("--no-move", action="store_true", help="Ablation: drop move planes.")
    parser.add_argument("--out", type=Path, default=RESULTS_CSV)
    parser.add_argument("--overwrite", action="store_true", help="Truncate the results CSV.")
    args = parser.parse_args(argv)

    rows = _train(args, use_move=not args.no_move)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    write_header = args.overwrite or not args.out.exists()
    with args.out.open("w" if args.overwrite else "a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=["variant", "head", "metric", "model", "majority_baseline"]
        )
        if write_header:
            writer.writeheader()
        writer.writerows(rows)
    print(f"appended {len(rows)} rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
