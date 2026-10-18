"""The tiny CNN used by the neural baseline (requires the optional ``torch`` extra).

Three heads share a small convolutional trunk: a softmax quality head over
``QUALITY_LABELS``, and sigmoid multi-label heads over ``THEME_VOCAB`` and ``INTENT_VOCAB``.
"""

from __future__ import annotations

import torch
from torch import nn

from ..config import INTENT_VOCAB, QUALITY_LABELS, THEME_VOCAB


class MoveNet(nn.Module):
    """Conv trunk + global pool, with quality, theme and intent heads.

    ``quality_mode`` selects the quality head's shape:

    * ``"classification"`` (default) -- a softmax over the discrete ``QUALITY_LABELS``;
    * ``"regression"`` -- a single scalar predicting ``loss_wp`` directly.

    The classification head is a poor fit for the quality label: the classes are extremely
    imbalanced (most moves are "best"), and "best" is defined by a rank/threshold rule rather
    than a natural category. Regressing the underlying ``loss_wp`` and deriving the label from
    the existing thresholds keeps the ordinal structure and avoids the arbitrary boundaries.
    """

    def __init__(
        self,
        in_planes: int,
        *,
        n_themes: int = len(THEME_VOCAB),
        n_intents: int = len(INTENT_VOCAB),
        n_quality: int = len(QUALITY_LABELS),
        channels: int = 32,
        hidden: int = 64,
        quality_mode: str = "classification",
    ) -> None:
        super().__init__()
        if quality_mode not in ("classification", "regression"):
            raise ValueError(
                f"quality_mode must be 'classification' or 'regression', got {quality_mode!r}"
            )
        self.quality_mode = quality_mode
        self.features = nn.Sequential(
            nn.Conv2d(in_planes, channels, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(channels, channels, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(channels, channels * 2, 3, padding=1),
            nn.ReLU(),
        )
        self.trunk = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(channels * 2, hidden),
            nn.ReLU(),
            nn.Dropout(0.2),
        )
        self.quality = nn.Linear(hidden, n_quality if quality_mode == "classification" else 1)
        self.themes = nn.Linear(hidden, n_themes)
        self.intent = nn.Linear(hidden, n_intents)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Return ``(quality, theme_logits, intent_logits)``.

        ``quality`` is class logits in classification mode and a ``(n, 1)`` scalar in
        regression mode.
        """
        hidden = self.trunk(self.features(x))
        return self.quality(hidden), self.themes(hidden), self.intent(hidden)
