"""Material detectors: capture, sacrifice, trade, simplification, promotion, promotion threat.

Every detector gets a positive and a negative case built from :func:`positions.board`, so a
broken fixture fails loudly instead of silently testing the wrong thing.
"""

from __future__ import annotations

import chess

from moveexp.analysis.themes.base import DetectionContext, detect
from moveexp.analysis.themes.material import (
    detect_capture,
    detect_promotion,
    detect_promotion_threat,
    detect_sacrifice,
    detect_simplification,
    detect_trade,
)
from positions import after, board


def _ctx(fen_board: chess.Board, san: str) -> DetectionContext:
    return DetectionContext.from_move(fen_board, fen_board.parse_san(san))


def _themes(fen_board: chess.Board, san: str) -> set[str]:
    return {hit.theme for hit in detect(fen_board, fen_board.parse_san(san))}


# ----------------------------------------------------------------------------- capture
def test_capture_fires_on_a_capture():
    b = board("wN@c3", "bP@d5", "wK@e1", "bK@e8")
    assert detect_capture(_ctx(b, "Nxd5")).theme == "capture"


def test_capture_does_not_fire_on_a_quiet_move():
    assert detect_capture(_ctx(chess.Board(), "e4")) is None


# --------------------------------------------------------------------------- sacrifice
def test_sacrifice_fires_when_a_queen_is_given_for_a_pawn():
    b = board("wQ@d1", "bP@d7", "bQ@d8", "wK@e1", "bK@e8")
    ctx = _ctx(b, "Qxd7")
    assert ctx.see.gain_cp < 0, "giving a queen for a defended pawn must lose the exchange"
    assert detect_sacrifice(ctx).theme == "sacrifice"


def test_sacrifice_does_not_fire_on_a_winning_capture():
    b = board("wN@c3", "bP@d5", "wK@e1", "bK@e8")
    assert detect_sacrifice(_ctx(b, "Nxd5")) is None


# --------------------------------------------------------------------------------- trade
def test_trade_fires_on_an_even_exchange():
    b = board("wN@c3", "bN@d5", "bN@f4", "wK@e1", "bK@e8")
    ctx = _ctx(b, "Nxd5")
    assert abs(ctx.see.gain_cp) <= 30, "knight for knight is an even exchange"
    assert detect_trade(ctx).theme == "trade"


def test_trade_does_not_fire_on_a_winning_capture_or_a_sacrifice():
    winning = board("wN@c3", "bP@d5", "wK@e1", "bK@e8")
    assert detect_trade(_ctx(winning, "Nxd5")) is None
    losing = board("wQ@d1", "bP@d7", "bQ@d8", "wK@e1", "bK@e8")
    assert detect_trade(_ctx(losing, "Qxd7")) is None


# ----------------------------------------------------------------------- simplification
def test_simplification_fires_on_a_minor_for_minor_trade():
    b = board("wN@c3", "bN@d5", "bN@f4", "wK@e1", "bK@e8")
    assert detect_simplification(_ctx(b, "Nxd5")).theme == "simplification"


def test_simplification_does_not_fire_on_a_pawn_swap():
    b = board("wP@e4", "bP@d5", "bP@c6", "wK@e1", "bK@e8")
    ctx = _ctx(b, "exd5")
    assert detect_trade(ctx).theme == "trade", "a pawn for pawn is still a trade"
    assert detect_simplification(ctx) is None, "a pawn swap does not simplify"


# ---------------------------------------------------------------------------- promotion
def test_promotion_fires_and_records_the_new_piece():
    b = board("wP@b7", "bR@a8", "wK@h1", "bK@h8")
    hit = detect_promotion(_ctx(b, "bxa8=Q+"))
    assert hit.theme == "promotion"
    assert "Q" in hit.evidence


def test_promotion_does_not_fire_on_an_ordinary_pawn_move():
    assert detect_promotion(_ctx(chess.Board(), "e4")) is None


# -------------------------------------------------------------------- promotion threat
def test_promotion_threat_fires_when_a_passed_pawn_is_close():
    b = board("wP@d5", "wK@e1", "bK@e8")
    assert detect_promotion_threat(_ctx(b, "d6")).theme == "promotion_threat"


def test_promotion_threat_needs_proximity():
    b = board("wP@d4", "wK@e1", "bK@e8")
    assert detect_promotion_threat(_ctx(b, "d5")) is None


def test_promotion_threat_needs_a_passed_pawn():
    b = board("wP@d6", "bP@e7", "wK@e1", "bK@e8")
    assert detect_promotion_threat(_ctx(b, "Ke2")) is None


# ---------------------------------------------------------------------------- registry
def test_material_detectors_are_registered_and_quiet_positions_stay_clean():
    # A quiet developing move from the initial position must not emit material themes.
    quiet = _themes(chess.Board(), "Nf3")
    assert not quiet & {
        "capture",
        "sacrifice",
        "trade",
        "simplification",
        "promotion",
        "promotion_threat",
    }
    # The scholars-mate capture fires "capture" through the whole registry.
    b = after("e4", "e5", "Bc4", "Nc6", "Qh5", "Nf6")
    assert "capture" in _themes(b, "Qxf7#")
