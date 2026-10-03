"""Pawn-structure detectors: passed/isolated/doubled/backward, islands and breaks."""

from __future__ import annotations

import chess

from moveexp.analysis.themes.base import DetectionContext
from moveexp.analysis.themes.structure import (
    detect_backward_pawn,
    detect_creates_isolated_pawn,
    detect_creates_passed_pawn,
    detect_doubled_pawn,
    detect_isolated_pawn,
    detect_passed_pawn,
    detect_pawn_break,
    detect_pawn_island,
)
from positions import board


def _ctx(b: chess.Board, san: str) -> DetectionContext:
    return DetectionContext.from_move(b, b.parse_san(san))


# ---------------------------------------------------------------------------- passed pawn
def test_passed_pawn_when_a_pawn_is_passed():
    b = board("wP@d4", "wK@e1", "bK@e8")
    assert detect_passed_pawn(_ctx(b, "d5")).theme == "passed_pawn"


def test_advancing_an_existing_passer_is_not_creating_one():
    b = board("wP@d4", "wK@e1", "bK@e8")
    assert detect_creates_passed_pawn(_ctx(b, "d5")) is None


def test_creates_passed_pawn_when_the_last_blocker_is_captured():
    b = board("wP@d4", "bP@c5", "wK@e1", "bK@e8")
    assert detect_creates_passed_pawn(_ctx(b, "dxc5")).theme == "creates_passed_pawn"


def test_no_passed_pawn_on_a_quiet_position():
    assert detect_passed_pawn(_ctx(chess.Board(), "e4")) is None


# -------------------------------------------------------------------------- isolated pawn
def test_isolated_pawn_when_a_pawn_has_no_neighbour():
    b = board("wP@d4", "wP@h4", "wK@e1", "bK@e8")
    assert detect_isolated_pawn(_ctx(b, "Kf1")).theme == "isolated_pawn"


def test_creates_isolated_pawn_when_a_capture_strands_a_pawn():
    b = board("wP@a2", "wP@b2", "bP@c3", "wK@e1", "bK@e8")
    assert detect_creates_isolated_pawn(_ctx(b, "bxc3")).theme == "creates_isolated_pawn"


def test_no_isolated_pawn_in_the_initial_position():
    assert detect_isolated_pawn(_ctx(chess.Board(), "e4")) is None


# --------------------------------------------------------------------------- doubled pawn
def test_doubled_pawn_when_two_pawns_share_a_file():
    b = board("wP@d4", "wP@d5", "wK@e1", "bK@e8")
    assert detect_doubled_pawn(_ctx(b, "Kf1")).theme == "doubled_pawn"


def test_no_doubled_pawn_with_one_pawn_per_file():
    b = board("wP@d4", "wK@e1", "bK@e8")
    assert detect_doubled_pawn(_ctx(b, "Kf1")) is None


# -------------------------------------------------------------------------- backward pawn
def test_backward_pawn_that_cannot_advance_and_is_unsupported():
    b = board("wP@c2", "wP@d4", "bP@c6", "bP@e6", "wK@e1", "bK@e8")
    assert detect_backward_pawn(_ctx(b, "Kf1")).theme == "backward_pawn"


def test_no_backward_pawn_in_the_initial_position():
    assert detect_backward_pawn(_ctx(chess.Board(), "e4")) is None


# ---------------------------------------------------------------------------- pawn island
def test_pawn_island_when_a_capture_splits_the_chain():
    b = board("wP@a2", "wP@b2", "bP@c3", "wK@e1", "bK@e8")
    assert detect_pawn_island(_ctx(b, "bxc3")).theme == "pawn_island"


def test_no_pawn_island_change_on_a_quiet_move():
    assert detect_pawn_island(_ctx(chess.Board(), "e4")) is None


# ------------------------------------------------------------------------------ pawn break
def test_pawn_break_when_a_pawn_attacks_an_enemy_pawn():
    b = board("wP@e4", "bP@d6", "wK@e1", "bK@e8")
    assert detect_pawn_break(_ctx(b, "e5")).theme == "pawn_break"


def test_no_pawn_break_for_a_non_pawn_move():
    assert detect_pawn_break(_ctx(chess.Board(), "Nf3")) is None
