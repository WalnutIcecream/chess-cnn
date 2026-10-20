"""Metrics shared by the training scripts (hand-rolled: ``sklearn`` is not a dependency).

Every metric here works on plain numpy arrays so the scripts can be exercised without torch,
and so there is exactly one definition of "macro F1" in the project. The quality head is a
single-label problem (:func:`accuracy`, :func:`macro_f1`, :func:`confusion_matrix`); the
theme and intent heads are multi-label (:func:`multilabel_micro_f1`,
:func:`multilabel_macro_f1`, :func:`per_label_f1`).
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "accuracy",
    "binary_f1",
    "confusion_matrix",
    "macro_f1",
    "multilabel_macro_f1",
    "multilabel_micro_f1",
    "per_label_f1",
    "quality_label_counts",
]


def accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Fraction of rows whose single label was predicted correctly."""
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
    """F1 of one binary column, or ``None`` when the column is all-zero in truth and prediction."""
    tp = int((true_col * pred_col).sum())
    fp = int(((1 - true_col) * pred_col).sum())
    fn = int((true_col * (1 - pred_col)).sum())
    if tp + fp + fn == 0:
        return None
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def binary_f1(true_col: np.ndarray, pred_col: np.ndarray) -> float:
    """F1 of one binary column, ``0.0`` when it is unused in both truth and prediction.

    The scalar form of :func:`_binary_f1`, for code that tunes one label at a time (the per-tag
    decision thresholds) and wants a number it can compare rather than an optional.
    """
    score = _binary_f1(true_col, pred_col)
    return 0.0 if score is None else score


def multilabel_micro_f1(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Micro F1 over all labels at once (dominated by the common labels)."""
    tp = int((y_true * y_pred).sum())
    fp = int(((1 - y_true) * y_pred).sum())
    fn = int((y_true * (1 - y_pred)).sum())
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def multilabel_macro_f1(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Macro F1 over the labels that occur, so rare tactics count as much as common ones."""
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
