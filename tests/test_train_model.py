"""Tests for the training script's metric helpers and figure emission.

The module is loaded by path (it lives in ``scripts/``); it imports torch, so the whole
module is skipped when the optional torch extra is absent.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from moveexp.config import INTENT_VOCAB, THEME_VOCAB  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location("train_model", ROOT / "scripts" / "train_model.py")
assert _SPEC is not None and _SPEC.loader is not None
train = importlib.util.module_from_spec(_SPEC)
sys.modules["train_model"] = train
_SPEC.loader.exec_module(train)


def test_accuracy_and_macro_f1_perfect_prediction() -> None:
    labels = np.array([0, 1, 2, 2])
    assert train.accuracy(labels, labels) == 1.0
    assert train.macro_f1(labels, labels, 3) == 1.0


def test_confusion_matrix_counts_pairs() -> None:
    y_true = np.array([0, 0, 1, 2])
    y_pred = np.array([0, 1, 1, 2])
    matrix = train.confusion_matrix(y_true, y_pred, 3)
    assert matrix.shape == (3, 3)
    assert matrix[0, 0] == 1 and matrix[0, 1] == 1
    assert matrix[1, 1] == 1 and matrix[2, 2] == 1
    assert int(matrix.sum()) == 4


def test_per_label_f1_none_for_unused_column() -> None:
    y = np.array([[1, 0], [1, 0]], dtype=np.float32)
    scores = train.per_label_f1(y, y)
    assert scores[0] == 1.0
    assert scores[1] is None


def test_quality_label_counts() -> None:
    counts = train.quality_label_counts(np.array([0, 0, 5]), 8)
    assert len(counts) == 8
    assert counts[0] == 2 and counts[5] == 1


def test_write_figures_emits_expected_files(tmp_path: Path) -> None:
    history = {"train_loss": [3.0, 2.6, 2.5], "val_loss": [3.1, 2.7, 2.6]}
    counts = [10, 5, 3, 2, 1, 1, 0, 0]
    confusion = np.diag([4, 3, 2, 1, 0, 0, 0, 0])
    theme_f1 = [0.5 if i % 2 else None for i in range(len(THEME_VOCAB))]
    intent_f1 = [0.3 if i % 3 else None for i in range(len(INTENT_VOCAB))]

    written = train._write_figures(
        tmp_path,
        history=history,
        quality_counts=counts,
        confusion=confusion,
        theme_f1=theme_f1,
        intent_f1=intent_f1,
    )
    names = {path.name for path in written}
    assert {
        "loss_curves.png",
        "label_distribution.png",
        "theme_f1.png",
        "intent_f1.png",
        "quality_confusion.png",
    } <= names
    assert all(path.stat().st_size > 0 for path in written)
    assert (tmp_path / "per_label_f1.csv").exists()
