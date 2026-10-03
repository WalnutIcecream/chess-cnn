"""King-safety detectors: exposes_king, shelters_king, weakens_opponent_king."""

from __future__ import annotations

import chess

from moveexp.analysis.themes.base import DetectionContext
from moveexp.analysis.themes.king_safety import (
    detect_exposes_king,
    detect_shelters_king,
    detect_weakens_opponent_king,
)
from positions import board


def _ctx(b: chess.Board, san: str) -> DetectionContext:
    return DetectionContext.from_move(b, b.parse_san(san))


def test_exposes_king_when_a_shield_pawn_steps_out():
    b = board("wK@g1", "wP@f2", "wP@g2", "wP@h2", "bK@e8")
    assert detect_exposes_king(_ctx(b, "g4")).theme == "exposes_king"


def test_shelters_king_when_the_king_moves_behind_a_pawn():
    b = board("wK@e1", "wP@g2", "wP@h2", "bK@e8")
    assert detect_shelters_king(_ctx(b, "Kf1")).theme == "shelters_king"


def test_weakens_opponent_king_when_pressure_is_added():
    b = board("bK@g8", "bP@f7", "bP@g7", "bP@h7", "wR@e1", "wK@a1")
    assert detect_weakens_opponent_king(_ctx(b, "Re8+")).theme == "weakens_opponent_king"


def test_no_king_safety_theme_on_a_neutral_move():
    b = chess.Board()
    ctx = _ctx(b, "a3")
    assert detect_exposes_king(ctx) is None
    assert detect_shelters_king(ctx) is None
    assert detect_weakens_opponent_king(ctx) is None
