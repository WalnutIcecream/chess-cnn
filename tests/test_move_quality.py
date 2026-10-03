"""Tests for Stage-1 move quality: eval deltas, win-probability loss and labels.

No engine required: ``assess_move`` only consumes ``LineInfo`` objects, so exact
threshold behaviour can be tested deterministically.
"""

from __future__ import annotations

import chess
import pytest

from moveexp.analysis.move_quality import (
    MoveQuality,
    assess_move,
    classify_loss,
    classify_special,
)
from moveexp.config import QUALITY_LABELS
from moveexp.engine.eval_utils import cp_to_win_prob
from moveexp.schema import LineInfo


# ------------------------------------------------------------------ label thresholds
@pytest.mark.parametrize(
    ("loss_wp", "expected"),
    [
        (0.0, "best"),
        (0.0049, "best"),
        (0.0051, "excellent"),
        (0.019, "excellent"),
        (0.021, "good"),
        (0.049, "good"),
        (0.051, "inaccuracy"),
        (0.099, "inaccuracy"),
        (0.101, "mistake"),
        (0.199, "mistake"),
        (0.201, "blunder"),
        (0.95, "blunder"),
    ],
)
def test_classify_loss_bands(loss_wp: float, expected: str):
    assert classify_loss(loss_wp) == expected


def test_rank_one_forces_best_regardless_of_loss():
    """A loss for a rank-1 move is an artefact of a deeper line, not a mistake."""
    assert classify_loss(0.4, rank=1) == "best"
    assert classify_loss(0.4, rank=2) == "blunder"


def test_every_core_label_is_reachable():
    labels = {classify_loss(x) for x in (0.0, 0.01, 0.03, 0.07, 0.15, 0.5)}
    assert labels <= set(QUALITY_LABELS)
    assert "best" in labels and "blunder" in labels


def test_custom_thresholds_are_honoured():
    strict = {
        "best": 0.0001,
        "excellent": 0.002,
        "good": 0.01,
        "inaccuracy": 0.02,
        "mistake": 0.05,
        "blunder": float("inf"),
    }
    assert classify_loss(0.001, thresholds=strict) == "excellent"


# ----------------------------------------------------------------------- assess_move
def test_best_move_has_no_loss(start_board: chess.Board, line_factory):
    move = chess.Move.from_uci("e2e4")
    lines = [
        line_factory(move="e2e4", cp=35, rank=1),
        line_factory(move="d2d4", cp=30, rank=2),
        line_factory(move="g1f3", cp=20, rank=3),
    ]
    quality = assess_move(start_board, move, lines)
    assert quality.label == "best"
    assert quality.rank == 1
    assert quality.played_in_multipv is True
    assert quality.loss_cp == pytest.approx(0.0)
    assert quality.loss_wp == pytest.approx(0.0)
    assert quality.best_move == "e2e4"
    assert quality.best_move_san == "e4"
    assert quality.eval_before_cp == pytest.approx(35.0)
    assert quality.eval_after_cp == pytest.approx(35.0)
    assert quality.n_lines == 3


def _after(*sans: str) -> chess.Board:
    """Position after playing ``sans`` from the start position (kept legal by construction)."""
    board = chess.Board()
    for san in sans:
        board.push_san(san)
    return board


def test_loss_is_measured_against_the_best_line(line_factory):
    """After 1.e4 d5 White plays Nf3 while the engine preferred c4."""
    board = _after("e4", "d5")
    move = board.parse_uci("g1f3")
    lines = [
        line_factory(move="c2c4", cp=120, rank=1),
        line_factory(move="g1f3", cp=15, rank=2),
        line_factory(move="f1c4", cp=10, rank=3),
    ]
    quality = assess_move(board, move, lines)
    assert quality.rank == 2
    # 105cp of eval is ~8.6 points of win probability: an inaccuracy, not a blunder.
    assert quality.label == "inaccuracy"
    assert quality.loss_cp == pytest.approx(105.0)
    assert quality.loss_wp == pytest.approx(cp_to_win_prob(120) - cp_to_win_prob(15), abs=1e-12)


def test_blunder_read_from_the_multipv_line(line_factory):
    """When the played move is in the MultiPV set its own line supplies the new eval."""
    board = _after("e4", "e5", "Qh5")  # Black to move
    move = chess.Move.from_uci("b8c6")  # ?? Black ignores the queen on h5
    lines_before = [
        line_factory(move="g8f6", cp=1000, rank=1, turn=chess.BLACK),
        line_factory(move="b8c6", cp=300, rank=2, turn=chess.BLACK),
    ]
    quality = assess_move(board, move, lines_before)
    assert quality.label == "blunder"
    assert quality.played_in_multipv is True
    assert quality.rank == 2
    assert quality.eval_before_cp == pytest.approx(1000.0)
    assert quality.eval_after_cp == pytest.approx(300.0)
    assert quality.loss_cp == pytest.approx(700.0)
    assert quality.loss_wp == pytest.approx(cp_to_win_prob(1000) - cp_to_win_prob(300), abs=1e-12)


def test_blunder_measured_with_the_after_search(line_factory):
    """A move outside the MultiPV set needs a second search, whose score must be negated."""
    board = _after("e4", "e5", "Qh5")  # Black to move
    move = chess.Move.from_uci("b8c6")  # ?? Black ignores the queen on h5
    lines_before = [line_factory(move="g8f6", cp=1000, rank=1, turn=chess.BLACK)]
    # After 1...Nc6?? White is winning: -300cp from White's point of view is +300cp for
    # the mover (Black), i.e. a 700cp swing from the +1000cp Black had.
    lines_after = [line_factory(move="h5e5", cp=-300, rank=1, turn=chess.WHITE)]
    quality = assess_move(board, move, lines_before, lines_after)
    assert quality.label == "blunder"
    assert quality.played_in_multipv is False
    assert quality.rank is None
    assert quality.eval_after_cp == pytest.approx(300.0)
    assert quality.loss_cp == pytest.approx(700.0)
    assert quality.loss_wp == pytest.approx(cp_to_win_prob(1000) - cp_to_win_prob(300), abs=1e-12)
    # A move the engine did not rank (rank is None here) is *not* forced to "best".
    assert quality.label != "best"


def test_missing_after_search_is_an_error_not_a_silent_zero():
    board = chess.Board()
    move = chess.Move.from_uci("e2e4")
    not_played = LineInfo(turn=chess.WHITE, move="d2d4", pv=["d2d4"], score_cp=20)
    with pytest.raises(ValueError, match="no after-search"):
        assess_move(board, move, [not_played])


def test_illegal_move_is_rejected(line_factory):
    board = chess.Board()
    with pytest.raises(ValueError, match="illegal move"):
        assess_move(board, chess.Move.from_uci("e2e5"), [line_factory()])


def test_black_to_move_position_is_handled_from_the_movers_view(line_factory):
    """The same tactical picture with Black to move must give mirrored numbers."""
    board = _after("e4", "d5", "Nf3")  # Black to move
    move = chess.Move.from_uci("d8d6")
    lines_before = [
        line_factory(move="d8d6", cp=-40, rank=1, turn=chess.BLACK),
        line_factory(move="c8g4", cp=-90, rank=2, turn=chess.BLACK),
    ]
    quality = assess_move(board, move, lines_before)
    assert board.turn == chess.BLACK
    assert quality.eval_before_cp == pytest.approx(-40.0)
    assert quality.win_prob_before == pytest.approx(cp_to_win_prob(-40))
    assert quality.win_prob_before < 0.5
    assert quality.label == "best"


def test_mate_line_is_folded_into_centipawns(line_factory):
    board = chess.Board()
    move = chess.Move.from_uci("e2e4")
    lines = [
        line_factory(move="e2e4", cp=None, mate=3, rank=1),
        line_factory(move="d2d4", cp=-500, rank=2),
    ]
    quality = assess_move(board, move, lines)
    assert quality.eval_before_cp == pytest.approx(10_000 - 3)
    assert quality.eval_after_cp == pytest.approx(10_000 - 3)
    # Mate distances still fold into centi-pawns for reporting, but the win probability of a
    # forced mate is a certainty rather than the logistic's saturated 0.996.
    assert quality.win_prob_before == 1.0
    assert quality.win_prob_after == 1.0
    assert quality.loss_wp == 0.0
    assert quality.label == "best"


def test_lower_bound_lines_do_not_corrupt_the_label(line_factory):
    """Aspiration lower bounds are dropped before ranking."""
    board = chess.Board()
    move = chess.Move.from_uci("e2e4")
    lines = [
        line_factory(move="d2d4", cp=400, rank=1, bound="lower"),
        line_factory(move="e2e4", cp=25, rank=2),
    ]
    quality = assess_move(board, move, lines)
    assert quality.eval_before_cp == pytest.approx(25.0)
    # The rank the engine reported is preserved (2) even though the lower-bound line was
    # dropped, so a human reading the audit can still see what the engine claimed.
    assert quality.rank == 2
    assert quality.n_lines == 1
    assert quality.played_in_multipv is True
    # Comparing against the best *complete* line is what keeps the label at "best".
    assert quality.label == "best"


def test_to_dict_is_json_friendly(line_factory):
    import json

    board = chess.Board()
    move = chess.Move.from_uci("e2e4")
    quality = assess_move(board, move, [line_factory(move="e2e4", cp=10, rank=1)])
    json.dumps(quality.to_dict())


# ------------------------------------------------------------------- special labels
def _quality(label: str, *, rank: int | None = 1, wp_before: float = 0.6) -> MoveQuality:
    return MoveQuality(
        label=label,
        eval_before_cp=100,
        eval_after_cp=90,
        win_prob_before=wp_before,
        win_prob_after=wp_before - 0.01,
        loss_cp=10,
        loss_wp=0.01,
        best_move="e2e4",
        best_move_san="e4",
        best_move_cp=100,
        best_move_wp=wp_before,
        rank=rank,
        n_lines=3,
        played_in_multipv=True,
    )


def test_great_needs_a_big_gap_to_the_second_best(line_factory):
    board = chess.Board()
    move = chess.Move.from_uci("e2e4")
    lines = [
        line_factory(move="e2e4", cp=200, rank=1),
        line_factory(move="d2d4", cp=-120, rank=2),
    ]
    assert classify_special(_quality("best"), board, move, lines) == "great"


def test_not_great_when_the_second_best_is_equally_good(line_factory):
    board = chess.Board()
    move = chess.Move.from_uci("e2e4")
    lines = [
        line_factory(move="e2e4", cp=30, rank=1),
        line_factory(move="d2d4", cp=28, rank=2),
    ]
    assert classify_special(_quality("best"), board, move, lines) is None


def test_brilliant_needs_a_confirmed_sacrifice(line_factory):
    board = chess.Board()
    move = chess.Move.from_uci("e2e4")
    lines = [line_factory(move="e2e4", cp=0, rank=1)]
    assert classify_special(_quality("excellent"), board, move, lines) is None
    assert (
        classify_special(_quality("excellent"), board, move, lines, sacrifice_confirmed=True)
        == "brilliant"
    )


def test_brilliant_is_refused_in_an_already_won_position(line_factory):
    board = chess.Board()
    move = chess.Move.from_uci("e2e4")
    lines = [line_factory(move="e2e4", cp=900, rank=1)]
    assert (
        classify_special(
            _quality("best", wp_before=0.97), board, move, lines, sacrifice_confirmed=True
        )
        is None
    )


def test_brilliant_is_refused_for_a_plain_recapture(line_factory):
    board = _after("e4", "d5", "exd5")
    move = chess.Move.from_uci("d8d5")  # recapture
    lines = [line_factory(move="d8d5", cp=0, rank=1, turn=chess.BLACK)]
    assert classify_special(_quality("best"), board, move, lines, sacrifice_confirmed=True) is None


def test_special_label_never_downgrades(line_factory):
    """A blunder is never rewritten into a fancier label."""
    board = chess.Board()
    move = chess.Move.from_uci("e2e4")
    lines = [
        line_factory(move="d2d4", cp=900, rank=1),
        line_factory(move="e2e4", cp=-400, rank=2),
    ]
    quality = _quality("blunder", rank=2)
    assert classify_special(quality, board, move, lines) is None
    assert quality.with_label("best").label == "best"
