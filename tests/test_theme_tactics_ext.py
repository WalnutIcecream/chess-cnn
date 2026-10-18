"""The puzzle-tag detectors added in ``themes/tactics_ext.py``.

Every detector gets a positive **and** a negative case on hand-built legal positions
(``tests/positions.board``), which is the rule for this project: a detector that cannot be
shown *not* to fire is not tested at all. The assertions check membership rather than exact
equality, because several motifs legitimately co-occur on one move.
"""

from __future__ import annotations

import chess

from moveexp.analysis.themes import register_all, run_all
from moveexp.analysis.themes.base import DetectionContext
from positions import board

register_all()


def _themes(b: chess.Board, uci: str, *continuation: str) -> set[str]:
    """Run the full detector layer on ``uci`` (with an optional known continuation)."""
    move = chess.Move.from_uci(uci)
    assert move in b.legal_moves, f"{uci} is not legal in {b.fen()}"
    ctx = DetectionContext.from_move(
        b, move, continuation=[chess.Move.from_uci(c) for c in continuation]
    )
    return {hit.theme for hit in run_all(ctx)}


# ------------------------------------------------------------------ static: simple facts
def test_en_passant_fires_only_for_an_en_passant_capture():
    ep = board("wK@e1", "bK@e8", "wP@e5", "bP@d5", turn=chess.WHITE, ep="d6")
    assert "en_passant" in _themes(ep, "e5d6")
    normal = board("wK@e1", "bK@e8", "wP@e5", "bP@d6", turn=chess.WHITE)
    assert "en_passant" not in _themes(normal, "e5d6")


def test_under_promotion_fires_for_everything_but_a_queen():
    b = board("wK@g1", "bK@g8", "wP@a7", turn=chess.WHITE)
    assert "under_promotion" in _themes(b, "a7a8n")
    assert "under_promotion" not in _themes(b, "a7a8q")


# ------------------------------------------------------------------ static: structure motifs
def test_capturing_defender_fires_when_the_capture_removes_the_only_guard():
    b = board("wK@g1", "bK@g8", "bN@d5", "bP@c6", "wB@b5", turn=chess.WHITE)
    assert "capturing_defender" in _themes(b, "b5c6")


def test_capturing_defender_negative_when_the_target_has_a_second_defender():
    # Same idea, but the knight on d5 is also defended by the queen, so c6 is not the *only* guard.
    b = board("wK@g1", "bK@g8", "bN@d5", "bP@c6", "bQ@d8", "wB@b5", turn=chess.WHITE)
    assert "capturing_defender" not in _themes(b, "b5c6")


def test_attacking_f2f7_fires_only_when_f7_becomes_attacked():
    b = board("wK@g1", "bK@e8", "bP@f7", "wN@c4", turn=chess.WHITE)
    assert "attacking_f2f7" in _themes(b, "c4e5")  # Ne5 attacks f7
    assert "attacking_f2f7" not in _themes(b, "c4a5")  # Na5 attacks nothing near f7


def test_defensive_move_saves_a_hanging_piece():
    b = board("wK@g1", "bK@g8", "wQ@d1", "bR@d5", turn=chess.WHITE)
    assert "defensive_move" in _themes(b, "d1a4")  # the queen escapes the rook
    assert "defensive_move" not in _themes(b, "g1h1")  # the queen stays hanging


def test_advanced_pawn_needs_an_advanced_passed_pawn():
    passed = board("wK@g1", "bK@g8", "wP@c6", "bP@h7", turn=chess.WHITE)
    assert "advanced_pawn" in _themes(passed, "c6c7")
    blocked = board("wK@g1", "bK@g8", "wP@b5", "bP@a7", turn=chess.WHITE)
    assert "advanced_pawn" not in _themes(blocked, "b5b6")  # a7 stops b6 being passed


def test_quiet_move_needs_a_new_threat_from_a_quiet_move():
    b = board("wK@g1", "bK@g8", "bQ@h5", "wN@d3", turn=chess.WHITE)
    assert "quiet_move" in _themes(b, "d3f4")  # Nf4 attacks the loose queen
    assert "quiet_move" not in _themes(b, "d3e5")  # quiet, but threatens nothing


def test_quiet_move_never_fires_on_a_capture():
    b = board("wK@g1", "bK@g8", "bQ@h5", "wN@d3", "bP@f4", turn=chess.WHITE)
    assert "quiet_move" not in _themes(b, "d3f4")  # Nxf4 is a capture


# ------------------------------------------------------------------ static: king patterns
def test_kingside_and_queenside_attack_track_the_enemy_king_wing():
    kingside = board("wK@e2", "bK@g8", "bP@f7", "bP@g7", "bP@h7", "wR@a1", turn=chess.WHITE)
    assert "kingside_attack" in _themes(kingside, "a1g1")
    assert "kingside_attack" not in _themes(kingside, "a1a4")

    queenside = board("wK@e2", "bK@b8", "bP@a7", "bP@b7", "bP@c7", "wR@h1", turn=chess.WHITE)
    assert "queenside_attack" in _themes(queenside, "h1c1")


def test_smothered_mate_fires_on_a_king_hemmed_in_by_its_own_pieces():
    b = board("wK@e1", "bK@h8", "bP@g7", "bP@h7", "bR@g8", "wN@d6", turn=chess.WHITE)
    assert "smothered_mate" in _themes(b, "d6f7")


def test_smothered_mate_negative_when_it_is_not_checkmate():
    # Same mating net, but the rook that blocks g8 is gone, so the king can escape.
    b = board("wK@e1", "bK@h8", "bP@g7", "bP@h7", "wN@d6", turn=chess.WHITE)
    assert "smothered_mate" not in _themes(b, "d6f7")


def test_zugzwang_fires_when_every_reply_loses_material():
    # After the bishop lands on b3 the black king is immobile: g8 is covered by the bishop on
    # b3, h7 by the knight on g5, g7 by its own pawn. Its only move, g7-g6, drops the pawn to
    # Kxg6 with no recapture, so every reply loses material.
    b = board("wK@f5", "wN@g5", "wB@a2", "bK@h8", "bP@g7", turn=chess.WHITE)
    assert "zugzwang" in _themes(b, "a2b3")


def test_zugzwang_negative_when_a_reply_is_safe():
    # The same net plus a black pawn on a7 whose advance costs nothing: not a bind.
    b = board("wK@f5", "wN@g5", "wB@a2", "bK@h8", "bP@g7", "bP@a7", turn=chess.WHITE)
    assert "zugzwang" not in _themes(b, "a2b3")


# ------------------------------------------------------------------ line-aware motifs
def test_attraction_needs_the_opponent_to_take_the_bait():
    b = board("wK@g1", "bK@e8", "bR@a5", "wR@a1", "wN@c3", turn=chess.WHITE)
    assert "attraction" in _themes(b, "c3b5", "a5b5", "a1a8")


def test_clearance_needs_the_follow_up_to_use_the_vacated_square():
    b = board("wK@g1", "bK@e8", "wN@b4", "wR@b1", "bP@h7", turn=chess.WHITE)
    assert "clearance" in _themes(b, "b4c6", "h7h6", "b1b8")  # vacated b4 is on the b-file

    off_line = board("wK@g1", "bK@e8", "wN@g4", "wR@b1", "bP@h7", turn=chess.WHITE)
    assert "clearance" not in _themes(off_line, "g4f6", "h7h6", "b1b8")


def test_intermezzo_needs_a_forcing_move_before_the_recapture():
    b = board("wK@g1", "bK@e8", "bR@a5", "wR@a1", turn=chess.WHITE)
    assert "intermezzo" in _themes(b, "a1a5", "e8d8", "a5a8")


def test_intermezzo_negative_when_the_opponent_recaptures_at_once():
    b = board("wK@g1", "bK@e8", "bR@a5", "bQ@a8", "wR@a1", turn=chess.WHITE)
    assert "intermezzo" not in _themes(b, "a1a5", "a8a5", "g1h1")


# ------------------------------------------------------------------ line-aware gating
def test_line_aware_detectors_stay_silent_without_a_continuation():
    b = board("wK@g1", "bK@e8", "bR@a5", "wR@a1", "wN@c3", turn=chess.WHITE)
    themes = _themes(b, "c3b5")
    assert not themes & {"attraction", "clearance", "intermezzo"}


def test_an_illegal_continuation_is_ignored_rather_than_raising():
    b = board("wK@g1", "bK@e8", "wN@b4", "wR@b1", "bP@h7", turn=chess.WHITE)
    # The first "reply" is not legal after Nc6, so the continuation is empty and the
    # line-aware detectors simply do not fire.
    assert "clearance" not in _themes(b, "b4c6", "a1a8", "b1b8")
