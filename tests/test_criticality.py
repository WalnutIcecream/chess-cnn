"""Tests for criticality signals (Section 5.6)."""

from __future__ import annotations

import chess
import pytest

from moveexp.analysis.criticality import (
    assess_criticality,
    gap_to_second_wp,
    is_forcing,
    sharpness,
)
from moveexp.engine.eval_utils import cp_to_win_prob, win_prob_to_cp

#: Bare kings and a white bishop on e2: Bb5+ is a check that captures nothing.
FEN_CHECK = "4k3/8/8/8/8/8/4B3/4K3 w - - 0 1"


def _after(*sans: str) -> chess.Board:
    """Position after playing ``sans`` from the start position.

    Hand-written FENs go stale the moment a pawn moves somewhere unexpected; replaying
    SAN keeps every test position legal by construction.
    """
    board = chess.Board()
    for san in sans:
        board.push_san(san)
    return board


def _line(
    line_factory,
    *,
    move: str,
    rank: int,
    wp: float | None = None,
    turn=chess.WHITE,
    mate=None,
    cp=None,
):
    """Build a line with the given centi-pawns, or the centi-pawns of ``wp``."""
    cp_value = cp if cp is not None else win_prob_to_cp(float(wp))
    return line_factory(move=move, cp=cp_value, mate=mate, rank=rank, turn=turn)


def _first_move_where(board: chess.Board, predicate) -> chess.Move:
    """First legal move satisfying ``predicate``, with a helpful failure message."""
    for move in board.legal_moves:
        if predicate(board, move):
            return move
    raise AssertionError(f"no matching move in {board.fen()}")


def _capture(board: chess.Board, move: chess.Move) -> bool:
    return board.is_capture(move)


def _check(board: chess.Board, move: chess.Move) -> bool:
    after = board.copy(stack=False)
    after.push(move)
    return after.is_check()


# ------------------------------------------------------------------ gap to second best
def test_gap_to_second_wp_is_the_difference_of_the_top_two(line_factory):
    lines = [
        _line(line_factory, move="a", wp=0.70, rank=1),
        _line(line_factory, move="b", wp=0.40, rank=2),
        _line(line_factory, move="c", wp=0.30, rank=3),
    ]
    assert gap_to_second_wp(lines) == pytest.approx(0.30, abs=1e-6)


def test_gap_needs_two_lines(line_factory):
    """A truncated MultiPV must not be reported as "the only move"."""
    lines = [_line(line_factory, move="a", wp=0.9, rank=1)]
    assert gap_to_second_wp(lines) == 0.0
    assert sharpness(lines) == 0.0


def test_gap_is_measured_from_the_requested_point_of_view(line_factory):
    """MultiPV ranks are only ordered for the side to move, so the gap is taken by value.

    Rank 1 is *White's* best continuation, which is also Black's worst. Asking for
    Black's point of view of White's lines therefore answers a different question: how far
    apart Black's two best continuations are (White's ranks 3 and 2, mirrored).
    """
    white_lines = [
        _line(line_factory, move="a", cp=200, rank=1),
        _line(line_factory, move="b", cp=-250, rank=2),
        _line(line_factory, move="c", cp=-500, rank=3),
    ]
    probs = sorted((cp_to_win_prob(cp) for cp in (200, -250, -500)), reverse=True)
    assert gap_to_second_wp(white_lines, mover=chess.WHITE) == pytest.approx(
        probs[0] - probs[1], abs=1e-9
    )

    mirrored = sorted((1 - p for p in probs), reverse=True)
    assert gap_to_second_wp(white_lines, mover=chess.BLACK) == pytest.approx(
        mirrored[0] - mirrored[1], abs=1e-9
    )
    assert gap_to_second_wp(white_lines, mover=chess.BLACK) < gap_to_second_wp(
        white_lines, mover=chess.WHITE
    )


def test_sharpness_is_the_spread_across_lines(line_factory):
    lines = [
        _line(line_factory, move="a", wp=0.95, rank=1),
        _line(line_factory, move="b", wp=0.50, rank=2),
        _line(line_factory, move="c", wp=0.30, rank=3),
    ]
    assert sharpness(lines) == pytest.approx(0.65, abs=1e-6)


# ------------------------------------------------------------------------- only move
def test_is_only_move_flag(line_factory):
    board = _after("e4", "d5")  # White to move
    move = board.parse_uci("g1f3")
    board_after = board.copy(stack=False)
    board_after.push(move)
    lines = [
        _line(line_factory, move="g1f3", wp=0.72, rank=1),
        _line(line_factory, move="c2c4", wp=0.45, rank=2),
    ]
    crit = assess_criticality(
        board, move, board_after, lines, win_prob_before=0.72, win_prob_after=0.70
    )
    assert crit.is_only_move is True
    assert crit.gap_to_second_wp == pytest.approx(0.27, abs=1e-6)
    assert crit.is_critical is True
    assert crit.n_lines == 2


def test_equal_candidates_are_not_an_only_move(line_factory):
    board = _after("e4", "d5")
    move = board.parse_uci("g1f3")
    board_after = board.copy(stack=False)
    board_after.push(move)
    lines = [
        _line(line_factory, move="g1f3", wp=0.52, rank=1),
        _line(line_factory, move="c2c4", wp=0.51, rank=2),
    ]
    crit = assess_criticality(
        board, move, board_after, lines, win_prob_before=0.52, win_prob_after=0.51
    )
    assert crit.is_only_move is False
    assert crit.sharpness < 0.30
    assert crit.is_critical is False


def test_critical_when_the_move_loses_a_lot(line_factory):
    """Sharpness stays low, but the played move swung the evaluation."""
    board = _after("e4", "d5")
    move = board.parse_uci("g1f3")
    board_after = board.copy(stack=False)
    board_after.push(move)
    lines = [
        _line(line_factory, move="c2c4", wp=0.60, rank=1),
        _line(line_factory, move="d2d3", wp=0.59, rank=2),
    ]
    crit = assess_criticality(
        board, move, board_after, lines, win_prob_before=0.60, win_prob_after=0.45
    )
    assert crit.is_only_move is False
    assert crit.sharpness < 0.30
    assert crit.is_critical is True


def test_critical_when_the_position_is_volatile(line_factory):
    board = _after("e4", "d5")
    move = board.parse_uci("g1f3")
    board_after = board.copy(stack=False)
    board_after.push(move)
    lines = [
        _line(line_factory, move="c2c4", wp=0.70, rank=1),
        _line(line_factory, move="d2d3", wp=0.55, rank=2),
        _line(line_factory, move="g1f3", wp=0.15, rank=3),
    ]
    crit = assess_criticality(
        board, move, board_after, lines, win_prob_before=0.70, win_prob_after=0.69
    )
    assert crit.sharpness == pytest.approx(0.55, abs=1e-6)
    assert crit.is_critical is True
    assert crit.is_only_move is False


# --------------------------------------------------------------------------- forcing
def test_forcing_capture():
    """After 1.e4 d5 the pawn on e4 can take: that move is forcing."""
    board = _after("e4", "d5")
    move = _first_move_where(board, _capture)
    board_after = board.copy(stack=False)
    board_after.push(move)
    forcing, reason = is_forcing(board, move, board_after, [])
    assert forcing is True
    assert "capture" in reason


def test_forcing_check():
    """Bb5+ gives check without capturing anything."""
    board = chess.Board(FEN_CHECK)
    move = _first_move_where(board, _check)
    assert not board.is_capture(move)
    board_after = board.copy(stack=False)
    board_after.push(move)
    forcing, reason = is_forcing(board, move, board_after, [])
    assert forcing is True
    assert "check" in reason


def test_not_forcing_quiet_move():
    board = _after("e4", "d5")
    move = board.parse_uci("g1f3")
    board_after = board.copy(stack=False)
    board_after.push(move)
    assert not board_after.is_check()
    forcing, reason = is_forcing(board, move, board_after, [])
    assert forcing is False
    assert reason == ""


def test_forcing_when_the_pv_is_a_mate(line_factory):
    board = _after("e4", "d5")
    move = board.parse_uci("g1f3")
    board_after = board.copy(stack=False)
    board_after.push(move)
    lines = [line_factory(move="g1f3", cp=None, mate=2, rank=1)]
    forcing, reason = is_forcing(board, move, board_after, lines)
    assert forcing is True
    assert "mates in 2" in reason


def test_long_mate_in_pv_is_not_automatically_forcing(line_factory):
    board = _after("e4", "d5")
    move = board.parse_uci("g1f3")
    board_after = board.copy(stack=False)
    board_after.push(move)
    lines = [line_factory(move="g1f3", cp=None, mate=9, rank=1)]
    forcing, _ = is_forcing(board, move, board_after, lines)
    assert forcing is False


def test_forcing_mate_reason_uses_the_movers_side(line_factory):
    """The engine says the mover is mated: still forcing, but stated from their side."""
    board = _after("e4", "d5")
    move = board.parse_uci("g1f3")
    board_after = board.copy(stack=False)
    board_after.push(move)
    lines = [line_factory(move="g1f3", cp=None, mate=-1, rank=1)]
    forcing, reason = is_forcing(board, move, board_after, lines)
    assert forcing is True
    assert "is mated in 1" in reason


# ------------------------------------------------------------------------ perspective
def test_black_to_move_criticality_is_mirrored(line_factory):
    board = _after("e4", "d5", "Nf3")  # Black to move
    move = board.parse_uci("b8c6")
    board_after = board.copy(stack=False)
    board_after.push(move)
    lines = [
        _line(line_factory, move="b8c6", wp=0.55, rank=1, turn=chess.BLACK),
        _line(line_factory, move="g8f6", wp=0.53, rank=2, turn=chess.BLACK),
    ]
    crit = assess_criticality(
        board, move, board_after, lines, win_prob_before=0.55, win_prob_after=0.54
    )
    assert crit.n_lines == 2
    assert crit.is_only_move is False
    assert crit.is_critical is False
    # Black winning 55% is the mirror image of White winning 45%.
    assert crit.gap_to_second_wp == pytest.approx(0.02, abs=1e-6)


def test_criticality_to_dict_is_serialisable():
    import json

    board = _after("e4", "d5")
    move = board.parse_uci("g1f3")
    board_after = board.copy(stack=False)
    board_after.push(move)
    crit = assess_criticality(board, move, board_after, [], win_prob_before=0.5, win_prob_after=0.5)
    assert json.loads(json.dumps(crit.to_dict()))["is_critical"] is False


def test_assess_criticality_does_not_mutate_the_board():
    board = _after("e4", "d5", "Nf3")
    before_fen = board.fen()
    move = board.parse_uci("b8c6")
    board_after = board.copy(stack=False)
    board_after.push(move)
    assess_criticality(board, move, board_after, [], win_prob_before=0.5, win_prob_after=0.5)
    assert board.fen() == before_fen
