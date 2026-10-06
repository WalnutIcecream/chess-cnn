"""Tests for the CNN (skipped automatically when the optional ``torch`` extra is absent)."""

from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")

from moveexp.config import INTENT_VOCAB, QUALITY_LABELS, THEME_VOCAB  # noqa: E402
from moveexp.model.network import MoveNet  # noqa: E402


def test_movenet_output_shapes() -> None:
    model = MoveNet(15, channels=8, hidden=16)
    quality, themes, intents = model(torch.zeros(4, 15, 8, 8))
    assert quality.shape == (4, len(QUALITY_LABELS))
    assert themes.shape == (4, len(THEME_VOCAB))
    assert intents.shape == (4, len(INTENT_VOCAB))


def test_movenet_gradients_flow() -> None:
    model = MoveNet(13, channels=8, hidden=16)
    quality, themes, intents = model(torch.randn(2, 13, 8, 8))
    (quality.sum() + themes.sum() + intents.sum()).backward()
    assert any(param.grad is not None for param in model.parameters())
