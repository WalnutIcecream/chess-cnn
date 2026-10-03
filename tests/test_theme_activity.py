"""Activity detectors: outpost, rook files/ranks, bishops, development, centre control."""

from __future__ import annotations

import chess

from moveexp.analysis.themes.activity import (
    detect_bad_bishop,
    detect_bishop_pair,
    detect_controls_center,
    detect_develops_piece,
    detect_outpost,
    detect_rook_open_file,
    detect_rook_semi_open_file,
    detect_rook_seventh,
)
from moveexp.analysis.themes.base import DetectionContext
from positions import board


def _ctx(b: chess.Board, san: str) -> DetectionContext:
    return DetectionContext.from_move(b, b.parse_san(san))


# -------------------------------------------------------------------------------- outpost
def test_outpost_when_a_knight_lands_on_a_supported_square():
    b = board("wN@c3", "wP@e4", "wK@e1", "bK@e8")
    assert detect_outpost(_ctx(b, "Nd5")).theme == "outpost"


def test_no_outpost_for_an_undeveloped_minor():
    assert detect_outpost(_ctx(chess.Board(), "Nf3")) is None


# ------------------------------------------------------------------------ rook open file
def test_rook_open_file_when_the_file_has_no_pawns():
    b = board("wR@a1", "wK@e1", "bK@e8")
    assert detect_rook_open_file(_ctx(b, "Rd1")).theme == "rook_open_file"


def test_no_rook_open_file_for_a_non_rook_move():
    assert detect_rook_open_file(_ctx(chess.Board(), "e4")) is None


# -------------------------------------------------------------------- rook semi-open file
def test_rook_semi_open_file_when_only_enemy_pawns_remain():
    b = board("wR@a1", "bP@a7", "wK@e1", "bK@e8")
    assert detect_rook_semi_open_file(_ctx(b, "Ra3")).theme == "rook_semi_open_file"


def test_no_rook_semi_open_file_for_a_non_rook_move():
    assert detect_rook_semi_open_file(_ctx(chess.Board(), "e4")) is None


# --------------------------------------------------------------------------- rook seventh
def test_rook_seventh_when_a_rook_reaches_rank_six():
    b = board("wR@a1", "wK@e1", "bK@e8")
    assert detect_rook_seventh(_ctx(b, "Ra7")).theme == "rook_seventh"


def test_no_rook_seventh_for_a_non_rook_move():
    assert detect_rook_seventh(_ctx(chess.Board(), "e4")) is None


# ---------------------------------------------------------------------------- bishop pair
def test_bishop_pair_when_both_bishops_remain():
    b = board("wB@c1", "wB@f1", "wK@e1", "bK@e8")
    assert detect_bishop_pair(_ctx(b, "Kf2")).theme == "bishop_pair"


def test_no_bishop_pair_with_a_single_bishop():
    b = board("wB@c1", "wK@e1", "bK@e8")
    assert detect_bishop_pair(_ctx(b, "Kf2")) is None


# ----------------------------------------------------------------------------- bad bishop
def test_bad_bishop_when_a_bishop_is_boxed_in():
    b = board("wB@c1", "wP@b2", "wP@d2", "wK@e1", "bK@e8")
    assert detect_bad_bishop(_ctx(b, "Kf2")).theme == "bad_bishop"


def test_not_bad_bishop_when_the_bishop_has_moves():
    b = board("wB@c1", "wK@e1", "bK@e8")
    assert detect_bad_bishop(_ctx(b, "Kf2")) is None


# ------------------------------------------------------------------------ develops piece
def test_develops_piece_when_a_minor_leaves_the_back_rank():
    assert detect_develops_piece(_ctx(chess.Board(), "Nf3")).theme == "develops_piece"


def test_no_develops_piece_for_a_pawn_move():
    assert detect_develops_piece(_ctx(chess.Board(), "e4")) is None


# ------------------------------------------------------------------------ controls centre
def test_controls_center_when_a_move_takes_the_center():
    assert detect_controls_center(_ctx(chess.Board(), "e4")).theme == "controls_center"


def test_no_controls_center_for_an_off_center_move():
    assert detect_controls_center(_ctx(chess.Board(), "a3")) is None
