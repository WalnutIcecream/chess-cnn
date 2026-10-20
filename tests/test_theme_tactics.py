"""Tactical detectors: every rule gets a positive and a negative case.

Positions are built piece by piece with :func:`positions.board` so an illegal fixture fails
loudly instead of silently testing the wrong thing. The "negative" cases are the important
half: they pin down that a rule does *not* fire on the neighbouring position that looks
almost the same (a real fork vs a hung fork, a pin vs a free piece, and so on).
"""

from __future__ import annotations

import chess

from moveexp.analysis.themes.base import DetectionContext
from moveexp.analysis.themes.tactics import (
    detect_back_rank_mate,
    detect_deflection,
    detect_discovered_attack,
    detect_discovered_check,
    detect_double_check,
    detect_fork,
    detect_hanging_piece,
    detect_hanging_piece_defended,
    detect_interference,
    detect_overloaded_defender,
    detect_pin,
    detect_skewer,
    detect_threat_created,
    detect_trapped_piece,
    detect_x_ray,
)
from positions import after, board


def _ctx(b: chess.Board, san: str) -> DetectionContext:
    return DetectionContext.from_move(b, b.parse_san(san))


# --------------------------------------------------------------------------------- fork
def test_fork_on_king_and_rook():
    b = board("wN@d5", "bR@e8", "bK@g8", "wK@g1")
    hit = detect_fork(_ctx(b, "Nf6"))
    assert hit.theme == "fork"
    assert "e8" in hit.squares and "g8" in hit.squares


def test_no_fork_when_only_one_target():
    b = board("wN@c3", "bN@e7", "wK@e1", "bK@e8")
    assert detect_fork(_ctx(b, "Nd5")) is None


# ---------------------------------------------------------------------------------- pin
def test_absolute_pin():
    b = board("wR@e1", "bN@e7", "bK@e8", "wK@h1")
    hit = detect_pin(_ctx(b, "Kh2"))
    assert hit.theme == "pin"
    assert hit.confidence == 1.0


def test_relative_pin():
    b = board("wB@b3", "bR@e6", "bP@f7", "wK@g1", "bK@e8")
    hit = detect_pin(_ctx(b, "Kf1"))
    assert hit.theme == "pin"


def test_no_pin_on_a_quiet_position():
    assert detect_pin(_ctx(chess.Board(), "e4")) is None


# ------------------------------------------------------------------------------- skewer
def test_skewer_valuable_front_cheap_behind():
    b = board("wR@a1", "bQ@a4", "bR@a8", "wK@e1", "bK@e8")
    assert detect_skewer(_ctx(b, "Kf1")).theme == "skewer"


def test_no_skewer_when_front_is_cheaper():
    # Front rook (500), back queen (900): that is an x-ray, not a skewer.
    b = board("wR@a1", "bR@a4", "bQ@a8", "wK@e1", "bK@e8")
    assert detect_skewer(_ctx(b, "Kf1")) is None


# -------------------------------------------------------------------------------- x-ray
def test_x_ray_when_the_move_creates_the_ray():
    # The rook arrives on the a-file, where the enemy rook screens the queen behind it.
    b = board("wR@h1", "bR@a4", "bQ@a8", "wK@e2", "bK@e8")
    assert detect_x_ray(_ctx(b, "Ra1")).theme == "x_ray"


def test_no_x_ray_for_a_ray_that_already_existed():
    # The x-ray is on the board before the move; it is not this move's doing, so it is not
    # this move's x-ray.
    b = board("wR@a1", "bR@a4", "bQ@a8", "wK@e2", "bK@e8")
    assert detect_x_ray(_ctx(b, "Kf1")) is None


def test_no_x_ray_when_the_front_piece_is_the_more_valuable_one():
    # Queen in front, rook behind: that ordering is a skewer's business, not an x-ray's.
    b = board("wR@h1", "bQ@a4", "bR@a8", "wK@e2", "bK@e8")
    assert detect_x_ray(_ctx(b, "Ra1")) is None


# --------------------------------------------------------------------- discovered attack
def test_discovered_attack_opens_a_slider():
    b = board("wB@b2", "wN@d4", "bR@g7", "wK@e1", "bK@e8")
    hit = detect_discovered_attack(_ctx(b, "Nb5"))
    assert hit.theme == "discovered_attack"


def test_no_discovered_attack_on_a_quiet_move():
    assert detect_discovered_attack(_ctx(chess.Board(), "e4")) is None


# --------------------------------------------------------------------- discovered check
def test_discovered_check_when_the_mover_does_not_check():
    b = board("wB@b2", "wN@d4", "bK@g7", "wK@e1")
    assert detect_discovered_check(_ctx(b, "Nb3")).theme == "discovered_check"


def test_no_discovered_check_for_a_direct_check():
    b = after("e4", "e5", "Bc4", "Nc6", "Qh5", "Nf6")
    assert detect_discovered_check(_ctx(b, "Qxf7#")) is None


# -------------------------------------------------------------------------- double check
def test_double_check_from_move_and_uncovered_piece():
    b = board("wB@b2", "wN@d4", "bK@g7", "wK@e1")
    assert detect_double_check(_ctx(b, "Nf5")).theme == "double_check"


def test_no_double_check_for_a_single_check():
    b = after("e4", "e5", "Bc4", "Nc6", "Qh5", "Nf6")
    assert detect_double_check(_ctx(b, "Qxf7#")) is None


# --------------------------------------------------------------------------- hanging piece
def test_hanging_piece_when_a_piece_is_left_en_prise():
    b = board("wN@d5", "bQ@a8", "wK@e1", "bK@e8")
    assert detect_hanging_piece(_ctx(b, "Nb6")).theme == "hanging_piece"


def test_no_hanging_piece_on_a_quiet_move():
    assert detect_hanging_piece(_ctx(chess.Board(), "e4")) is None


# ------------------------------------------------------------------ hanging piece defended
def test_hanging_piece_defended_when_a_defender_arrives():
    b = board("wQ@d4", "bR@d8", "wP@c2", "wK@e1", "bK@e8")
    assert detect_hanging_piece_defended(_ctx(b, "c3")).theme == "hanging_piece_defended"


def test_no_hanging_piece_defended_on_a_quiet_move():
    assert detect_hanging_piece_defended(_ctx(chess.Board(), "e4")) is None


# --------------------------------------------------------------------------- threat created
def test_threat_created_when_a_defended_piece_is_attacked():
    b = board("wN@e2", "bQ@d5", "bP@e6", "wK@e1", "bK@e8")
    assert detect_threat_created(_ctx(b, "Nf4")).theme == "threat_created"


def test_no_threat_created_on_a_quiet_move():
    assert detect_threat_created(_ctx(chess.Board(), "e4")) is None


# --------------------------------------------------------------------------- back rank mate
def test_back_rank_mate():
    b = board("bK@g8", "bP@f7", "bP@g7", "bP@h7", "wR@e1", "wK@a1")
    assert detect_back_rank_mate(_ctx(b, "Re8#")).theme == "back_rank_mate"


def test_no_back_rank_mate_without_mate():
    assert detect_back_rank_mate(_ctx(chess.Board(), "e4")) is None


# --------------------------------------------------------------------------- trapped piece
def test_trapped_piece_when_every_escape_is_covered():
    b = board("bN@a8", "wR@a1", "wN@d5", "wK@e1", "bK@e8")
    assert detect_trapped_piece(_ctx(b, "Kf1")).theme == "trapped_piece"


def test_not_trapped_when_an_escape_is_free():
    b = board("bN@a8", "wB@g2", "wK@e1", "bK@e8")
    assert detect_trapped_piece(_ctx(b, "Kf1")) is None


# ---------------------------------------------------------------------- overloaded defender
def test_overloaded_defender_defends_two_attacked_pieces():
    b = board("bR@d4", "bN@b4", "bN@f4", "wR@b1", "wR@f1", "wK@h1", "bK@e8")
    hit = detect_overloaded_defender(_ctx(b, "Kg1"))
    assert hit.theme == "overloaded_defender"
    assert "b4" in hit.squares and "f4" in hit.squares


def test_not_overloaded_when_a_second_defender_exists():
    # The rook no longer alone defends b4: the black king (b5, adjacent to b4) also guards it.
    b = board("bR@d4", "bN@b4", "bN@f4", "wR@b1", "wR@f1", "wK@h1", "bK@b5")
    assert detect_overloaded_defender(_ctx(b, "Kg1")) is None


# ----------------------------------------------------------------------------- deflection
def test_deflection_when_the_guard_is_attacked():
    b = board("wN@g1", "bR@d4", "bN@b4", "wR@b1", "wK@e1", "bK@e8")
    assert detect_deflection(_ctx(b, "Nf3")).theme == "deflection"


def test_no_deflection_on_a_quiet_move():
    assert detect_deflection(_ctx(chess.Board(), "e4")) is None


# ---------------------------------------------------------------------------- interference
def test_interference_when_a_move_blocks_an_enemy_slider():
    b = board("bR@a8", "wR@a1", "wN@b1", "wK@e1", "bK@e8")
    assert detect_interference(_ctx(b, "Na3")).theme == "interference"


def test_no_interference_on_a_quiet_move():
    assert detect_interference(_ctx(chess.Board(), "e4")) is None
