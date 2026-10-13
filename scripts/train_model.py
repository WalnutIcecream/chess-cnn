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

from moveexp.config import (
    INTENT_VOCAB,
    PROJECT_ROOT,
    QUALITY_LABELS,
    SPLIT_FRACTIONS,
    THEME_VOCAB,
)
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


def confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, n_classes: int) -> np.ndarray:
    """Counts of ``(true, predicted)`` pairs, shape ``(n_classes, n_classes)``."""
    matrix = np.zeros((n_classes, n_classes), dtype=np.int64)
    np.add.at(matrix, (y_true.astype(int), y_pred.astype(int)), 1)
    return matrix


def per_label_f1(y_true: np.ndarray, y_pred: np.ndarray) -> list[float | None]:
    """Per-column F1 for binary multi-label arrays (``None`` when a column is unused)."""
    return [_binary_f1(y_true[:, col], y_pred[:, col]) for col in range(y_true.shape[1])]


def quality_label_counts(labels: np.ndarray, n_classes: int) -> list[int]:
    """How many rows carry each quality class."""
    return np.bincount(labels.astype(int), minlength=n_classes).tolist()


# --------------------------------------------------------------------------------------
# Figures (matplotlib, imported lazily so importing this module stays light)
# --------------------------------------------------------------------------------------


def _f1_bar(
    path: Path, names: tuple[str, ...], scores: list[float | None], title: str, color: str
) -> None:
    """Horizontal bar chart of per-label F1, most useful labels first."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    pairs = [(name, score) for name, score in zip(names, scores, strict=True) if score is not None]
    pairs.sort(key=lambda item: item[1], reverse=True)
    labels = [name for name, _ in pairs]
    values = [score for _, score in pairs]
    height = max(2.2, 0.24 * len(pairs) + 0.7)
    fig, ax = plt.subplots(figsize=(7.6, height))
    ax.barh(range(len(values)), values, color=color)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=7.5)
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.set_xlabel("F1", fontsize=9)
    ax.set_title(title, fontsize=10)
    ax.grid(axis="x", linestyle=":", color="#c9d0da")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def _write_figures(
    figures_dir: Path,
    *,
    history: dict[str, list[float]],
    quality_counts: list[int],
    confusion: np.ndarray,
    theme_f1: list[float | None],
    intent_f1: list[float | None],
) -> list[Path]:
    """Write the training/process figures and the per-label F1 table. Returns the paths."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figures_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    epochs = range(1, len(history["train_loss"]) + 1)
    fig, ax = plt.subplots(figsize=(7.6, 3.4))
    ax.plot(epochs, history["train_loss"], label="train", color="#3f8f5f")
    ax.plot(epochs, history["val_loss"], label="validation", color="#c0653a")
    ax.set_xlabel("epoch", fontsize=9)
    ax.set_ylabel("loss", fontsize=9)
    ax.set_title("Training and validation loss", fontsize=10)
    ax.legend(fontsize=8.5)
    ax.grid(linestyle=":", color="#c9d0da")
    path = figures_dir / "loss_curves.png"
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    written.append(path)

    fig, ax = plt.subplots(figsize=(7.6, 3.4))
    ax.bar(range(len(QUALITY_LABELS)), quality_counts, color="#4a7fb5")
    ax.set_xticks(range(len(QUALITY_LABELS)))
    ax.set_xticklabels(QUALITY_LABELS, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("moves", fontsize=9)
    ax.set_title("Move-quality label distribution (all labelled moves)", fontsize=10)
    for index, count in enumerate(quality_counts):
        if count:
            ax.text(index, count, str(count), ha="center", va="bottom", fontsize=7.5)
    path = figures_dir / "label_distribution.png"
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    written.append(path)

    theme_path = figures_dir / "theme_f1.png"
    _f1_bar(theme_path, THEME_VOCAB, theme_f1, "Per-theme F1 on held-out games", "#3f8f5f")
    written.append(theme_path)
    intent_path = figures_dir / "intent_f1.png"
    _f1_bar(intent_path, INTENT_VOCAB, intent_f1, "Per-intent F1 on held-out games", "#8a6fb5")
    written.append(intent_path)

    present = [i for i in range(len(QUALITY_LABELS)) if confusion[i].sum() > 0]
    sub = confusion[np.ix_(present, present)].astype(float)
    row = sub / np.maximum(sub.sum(axis=1, keepdims=True), 1.0)
    fig, ax = plt.subplots(figsize=(6.2, 5.2))
    image = ax.imshow(row, cmap="Blues", vmin=0, vmax=1)
    ticks = range(len(present))
    ax.set_xticks(list(ticks))
    ax.set_xticklabels([QUALITY_LABELS[i] for i in present], rotation=45, ha="right", fontsize=8)
    ax.set_yticks(list(ticks))
    ax.set_yticklabels([QUALITY_LABELS[i] for i in present], fontsize=8)
    ax.set_xlabel("predicted", fontsize=9)
    ax.set_ylabel("true", fontsize=9)
    ax.set_title("Quality confusion (row-normalised)", fontsize=10)
    for r in ticks:
        for c in ticks:
            ax.text(c, r, f"{row[r, c]:.2f}", ha="center", va="center", fontsize=7, color="#16202e")
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    path = figures_dir / "quality_confusion.png"
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    written.append(path)

    with (figures_dir / "per_label_f1.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["head", "label", "f1"])
        for name, score in zip(THEME_VOCAB, theme_f1, strict=True):
            writer.writerow(["theme", name, "" if score is None else f"{score:.4f}"])
        for name, score in zip(INTENT_VOCAB, intent_f1, strict=True):
            writer.writerow(["intent", name, "" if score is None else f"{score:.4f}"])

    return written


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
    history: dict[str, list[float]] = {"train_loss": [], "val_loss": []}
    for _epoch in range(args.epochs):
        model.train()
        order = torch.randperm(len(train))
        epoch_loss = 0.0
        batches = 0
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
            epoch_loss += float(loss.detach())
            batches += 1
        model.eval()
        with torch.no_grad():
            q_logits, t_logits, i_logits = model(x_val)
            val_loss = float(
                cross_entropy(q_logits, yq_val)
                + bce(t_logits, yt_val)
                + intent_bce(i_logits, yi_val)
            )
        history["train_loss"].append(epoch_loss / max(batches, 1))
        history["val_loss"].append(val_loss)
        if val_loss < best_val:
            best_val = val_loss
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
    model.load_state_dict(best_state)

    if args.save is not None:
        args.save.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "state_dict": model.state_dict(),
                "in_planes": x.shape[1],
                "channels": args.channels,
                "hidden": args.hidden,
                "variant": "with_move" if use_move else "without_move",
            },
            args.save,
        )
        print(f"  saved checkpoint to {args.save}")

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

    if args.figures_dir is not None:
        written = _write_figures(
            args.figures_dir,
            history=history,
            quality_counts=quality_label_counts(y_quality, len(QUALITY_LABELS)),
            confusion=confusion_matrix(yq_test_np, q_pred, len(QUALITY_LABELS)),
            theme_f1=per_label_f1(yt_test_np, t_pred),
            intent_f1=per_label_f1(yi_test_np, i_pred),
        )
        print(f"  figures: wrote {len(written)} files to {args.figures_dir}")

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
    parser.add_argument(
        "--figures-dir",
        type=Path,
        default=None,
        help="Write training/process figures here (loss curves, label distribution, "
        "per-label F1, confusion matrix).",
    )
    parser.add_argument(
        "--save",
        type=Path,
        default=None,
        help="Save the best-validation model checkpoint here (used by the process gallery).",
    )
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
