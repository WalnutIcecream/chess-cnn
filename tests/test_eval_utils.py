"""Tests for the score / win-probability conversions and the perspective rule.

These are the tests that matter most in the whole project: mixing white-perspective and
mover-perspective numbers is the classic way to get plausible-looking but wrong labels.
"""

from __future__ import annotations

import math

import chess
import chess.engine
import pytest

from conftest import mirror_fen
from moveexp.config import MATE_CP_BASE, WIN_PROB_CP_SCALE
from moveexp.engine import eval_utils
from moveexp.engine.eval_utils import (
    best_line,
    cp_to_win_prob,
    find_rank,
    line_win_prob,
    lines_to_mover_perspective,
    mate_to_cp,
    pov_to_mover_cp,
    score_to_cp,
    to_mover_perspective,
    win_prob_to_cp,
    win_probs,
)


# --------------------------------------------------------------------------- win prob
def test_cp_to_win_prob_matches_the_specified_formula():
    """The implementation is exactly the documented logistic, with clamping applied."""
    for cp in (-1200, -300, -37, 0, 37, 300, 1200):
        expected = 1.0 / (1.0 + math.exp(-WIN_PROB_CP_SCALE * cp))
        assert cp_to_win_prob(cp) == pytest.approx(expected, rel=1e-12)


def test_cp_to_win_prob_is_half_at_zero_and_monotone():
    assert cp_to_win_prob(0.0) == pytest.approx(0.5)
    previous = -1.0
    for cp in range(-1500, 1501, 25):
        current = cp_to_win_prob(cp)
        assert current > previous
        previous = current


def test_cp_to_win_prob_clamps_large_values():
    """Beyond the clamp the probability saturates instead of collapsing to 0/1."""
    assert cp_to_win_prob(50_000) == pytest.approx(cp_to_win_prob(1500))
    assert cp_to_win_prob(-50_000) == pytest.approx(cp_to_win_prob(-1500))
    assert 0.0 < cp_to_win_prob(1500) < 1.0


def test_win_prob_to_cp_inverts_cp_to_win_prob():
    for cp in (-800, -100, 0, 100, 800):
        assert win_prob_to_cp(cp_to_win_prob(cp)) == pytest.approx(cp, abs=1e-6)


# ------------------------------------------------------------------------------ mates
@pytest.mark.parametrize(
    ("mate", "expected"),
    [
        (1, MATE_CP_BASE - 1),
        (3, MATE_CP_BASE - 3),
        (-3, -(MATE_CP_BASE - 3)),
        (0, -float(MATE_CP_BASE)),
    ],
)
def test_mate_folding(mate: int, expected: float):
    """Mate in N -> +10000 - N, mated in N -> -10000 + N."""
    assert mate_to_cp(mate) == expected


def test_mate_folding_is_antisymmetric():
    for n in range(1, 8):
        assert mate_to_cp(-n) == -mate_to_cp(n)


def test_score_to_cp_handles_cp_and_mate():
    assert score_to_cp(chess.engine.Cp(-45)) == pytest.approx(-45.0)
    assert score_to_cp(chess.engine.Mate(2)) == pytest.approx(float(MATE_CP_BASE - 2))
    # python-chess reports mate() == 0 for both "mated" and "mate given"; the two are only
    # distinguishable by their type, and they must not fold to the same centi-pawn value.
    assert score_to_cp(chess.engine.MateGiven) == pytest.approx(float(MATE_CP_BASE))
    assert score_to_cp(chess.engine.Mate(0)) == pytest.approx(-float(MATE_CP_BASE))


def test_cp_from_mate_keeps_the_raw_distance():
    cp, mate = eval_utils.cp_from_mate(-4)
    assert cp == pytest.approx(-(MATE_CP_BASE - 4))
    assert mate == -4


# ------------------------------------------------------------------------- perspective
def test_to_mover_perspective_is_identity_for_the_side_to_move():
    score = chess.engine.PovScore(chess.engine.Cp(120), chess.WHITE)
    assert to_mover_perspective(score, chess.WHITE).relative.score() == 120


def test_to_mover_perspective_negates_for_the_other_side():
    score = chess.engine.PovScore(chess.engine.Cp(120), chess.WHITE)
    moved = to_mover_perspective(score, chess.BLACK)
    assert moved.relative.score() == -120
    assert moved.turn == chess.BLACK


def test_mate_sign_follows_the_mating_side():
    """A mate that is positive for White is negative for Black, because Black is mated."""
    white_mates = chess.engine.PovScore(chess.engine.Mate(3), chess.WHITE)
    assert to_mover_perspective(white_mates, chess.BLACK).relative.mate() == -3
    black_mates = chess.engine.PovScore(chess.engine.Mate(3), chess.BLACK)
    assert to_mover_perspective(black_mates, chess.WHITE).relative.mate() == -3


def test_mirrored_positions_give_mirrored_mover_values():
    """Same position, colours swapped: the mover's win probability must mirror exactly."""
    white_to_move = chess.engine.PovScore(chess.engine.Cp(240), chess.WHITE)
    black_to_move = chess.engine.PovScore(chess.engine.Cp(240), chess.BLACK)

    # The engine reports the same relative score either way; only the perspective differs.
    assert cp_to_win_prob(pov_to_mover_cp(white_to_move, chess.WHITE)[0]) == pytest.approx(
        cp_to_win_prob(240)
    )
    assert cp_to_win_prob(pov_to_mover_cp(black_to_move, chess.WHITE)[0]) == pytest.approx(
        cp_to_win_prob(-240)
    )


def test_pov_to_mover_cp_returns_cp_and_mate_separately():
    cp_score = chess.engine.PovScore(chess.engine.Cp(-80), chess.BLACK)
    assert pov_to_mover_cp(cp_score, chess.WHITE) == (pytest.approx(80.0), None)
    mate_score = chess.engine.PovScore(chess.engine.Mate(5), chess.BLACK)
    cp, mate = pov_to_mover_cp(mate_score, chess.WHITE)
    assert mate == -5
    assert cp == pytest.approx(-(MATE_CP_BASE - 5))


def test_to_mover_perspective_rejects_plain_scores():
    with pytest.raises(TypeError):
        to_mover_perspective(chess.engine.Cp(10), chess.WHITE)  # type: ignore[arg-type]


# ------------------------------------------------------------------------------- lines
def test_lines_to_mover_perspective_flips_cp_and_mate(line_factory):
    lines = [
        line_factory(move="a7a8q", cp=None, mate=2, rank=1, turn=chess.WHITE),
        line_factory(move="a7a5", cp=-30, rank=2, turn=chess.WHITE),
    ]
    flipped = lines_to_mover_perspective(lines, chess.BLACK)
    assert flipped[0].turn is chess.BLACK
    # `mate` flips sign (the mating side flipped); `score_cp` stays empty because the raw
    # line carries no centi-pawn value, which is what `line_eval_cp` folds in.
    assert flipped[0].mate == -2
    assert flipped[0].score_cp is None
    assert eval_utils.line_eval_cp(flipped[0]) == pytest.approx(-float(MATE_CP_BASE - 2))
    assert flipped[1].score_cp == pytest.approx(30.0)


def test_lines_to_mover_perspective_is_idempotent(line_factory):
    lines = [line_factory(cp=90, turn=chess.BLACK)]
    once = lines_to_mover_perspective(lines, chess.BLACK)
    twice = lines_to_mover_perspective(once, chess.BLACK)
    assert once[0].score_cp == twice[0].score_cp == pytest.approx(90.0)


def test_best_line_skips_lower_bounds_and_ranks(line_factory):
    lines = [
        line_factory(move="e2e4", cp=10, rank=2),
        line_factory(move="d2d4", cp=900, rank=1, bound="lower"),
        line_factory(move="c2c4", cp=5, rank=3),
    ]
    # Rank 1 is an optimistic aspiration bound, so the best *usable* line is rank 2.
    assert best_line(lines).move == "e2e4"
    assert best_line([]) is None


def test_find_rank(line_factory):
    lines = [
        line_factory(move="e2e4", rank=1),
        line_factory(move="d2d4", rank=2),
        line_factory(move="g1f3", rank=3),
    ]
    assert find_rank(lines, "d2d4") == 2
    assert find_rank(lines, "b1c3") is None


def test_win_probs_orders_by_rank_and_folds_mates(line_factory):
    lines = [
        line_factory(move="c", cp=-100, rank=3),
        line_factory(move="a", cp=None, mate=1, rank=1),
        line_factory(move="b", cp=40, rank=2),
    ]
    assert win_probs(lines) == pytest.approx([1.0, cp_to_win_prob(40), cp_to_win_prob(-100)])


def test_line_win_prob_treats_forced_mate_as_certainty(line_factory):
    """A mate line is 1.0/0.0, not the logistic's saturated 0.996."""
    won = line_factory(move="a", cp=None, mate=1)
    lost = line_factory(move="b", cp=None, mate=-4)
    unknown = line_factory(move="c", cp=None, mate=None)
    assert line_win_prob(won) == 1.0
    assert line_win_prob(lost) == 0.0
    assert line_win_prob(unknown) == 0.5, "an unscored line must stay neutral"
    assert line_win_prob(line_factory(move="d", cp=120)) == pytest.approx(cp_to_win_prob(120))


def test_cache_key_ignores_move_counters():
    """Two FENs that differ only in the halfmove/fullmove counters share a cache key."""
    from moveexp.engine.cache import make_cache_key

    a = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    b = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 47 92"
    assert make_cache_key(a, "d16", 3) == make_cache_key(b, "d16", 3)
    assert make_cache_key(a, "d16", 3) != make_cache_key(a, "d18", 3)
    assert make_cache_key(a, "d16", 3) != make_cache_key(a, "d16", 5)
    # Results from different engine versions must never share a key.
    assert make_cache_key(a, "d16", 3, engine_version="Stockfish 19") != make_cache_key(
        a, "d16", 3, engine_version="Stockfish 18"
    )


def test_mirror_fen_helper_is_an_involution():
    # A middlegame position whose mirror is also legal: mirroring can create checks that
    # were not there, so this fixture is chosen to avoid them.
    fen = "r1bq1rk1/pp3ppp/2np1n2/2p1p3/2P1P3/2NP1N2/PP3PPP/R1BQ1RK1 w - - 0 10"
    assert mirror_fen(mirror_fen(fen)) == fen
    board = chess.Board(fen)
    mirrored = chess.Board(mirror_fen(fen))
    assert mirrored.turn != board.turn
    assert mirrored.is_valid()
