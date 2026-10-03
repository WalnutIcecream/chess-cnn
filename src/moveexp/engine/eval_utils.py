"""Conversion between engine scores, centi-pawns, win probability and perspectives.

**This is the only module allowed to change the point of view of an engine score.**
Everything downstream (``analysis``, ``themes``, ``features``, the dataset, the model
targets) works in the *mover's* point of view, so mixing perspectives is impossible as
long as callers go through the helpers here.

Reference conventions
---------------------
* Stockfish reports a score from the point of view of the side to move of the analysed
  position, as a :class:`chess.engine.PovScore`.
* :func:`to_mover_perspective` returns the same game score from the point of view of an
  arbitrary colour. It is a plain negation for centi-pawns; for mate scores the sign of
  the distance flips, which is correct because the *mating side* also flips.
* :func:`cp_to_win_prob` is the logistic model used by Lichess to display Stockfish
  evaluations. Win probability is what quality labels and criticality thresholds use,
  because centi-pawn deltas are not perceptually linear.

**Assumption (stated, not verifiable from the python-chess docs):** python-chess copies
Stockfish's ``score mate N`` value straight into :class:`chess.engine.Mate` without unit
conversion, while ``Score.mate()`` is documented as "plies to mate". Stockfish reports
mate distances in *moves*, not plies. Nothing in this project depends on the unit: the
raw value is preserved in ``LineInfo.mate`` and :func:`mate_to_cp` only uses it as a
magnitude, so a factor-of-two error would at worst double the mate distance reported to
a human reader. Use :func:`cp_from_mate` with an explicit ``units_per_ply`` if you ever
need real plies.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Final

import chess
import chess.engine

from ..config import (
    MATE_CP_BASE,
    WIN_PROB_CP_CLAMP,
    WIN_PROB_CP_SCALE,
)
from ..schema import LineInfo

__all__ = [
    "cp_to_win_prob",
    "line_eval_cp",
    "line_win_prob",
    "win_prob_to_cp",
    "mate_to_cp",
    "cp_from_mate",
    "score_to_cp",
    "to_mover_perspective",
    "pov_to_mover_cp",
    "line_to_mover_perspective",
    "lines_to_mover_perspective",
    "best_line",
    "find_rank",
    "win_prob_gap_to_second",
    "win_probs",
]


def clamp_cp(cp: float, *, clamp: float = WIN_PROB_CP_CLAMP) -> float:
    """Clamp centi-pawns into the range the win-probability model is fitted on."""
    return max(-clamp, min(clamp, float(cp)))


def cp_to_win_prob(
    cp: float, *, scale: float = WIN_PROB_CP_SCALE, clamp: float = WIN_PROB_CP_CLAMP
) -> float:
    """Convert centi-pawns to the probability that the side to move wins.

    ``P = 1 / (1 + exp(-scale * cp))`` after clamping ``cp`` to +/- ``clamp``.
    ``cp_to_win_prob(0) == 0.5``, values are monotone and the result is in ``(0, 1)``.

    :param cp: evaluation in centi-pawns, positive in favour of the mover.
    """
    value = clamp_cp(cp, clamp=clamp)
    return 1.0 / (1.0 + math.exp(-scale * value))


def win_prob_to_cp(
    prob: float, *, scale: float = WIN_PROB_CP_SCALE, clamp: float = WIN_PROB_CP_CLAMP
) -> float:
    """Inverse of :func:`cp_to_win_prob` (used to sanity-check thresholds, in tests)."""
    prob = min(max(float(prob), 1e-6), 1 - 1e-6)
    cp = -math.log(1.0 / prob - 1.0) / scale
    return max(-clamp, min(clamp, cp))


def mate_to_cp(mate: int, *, mate_cp_base: int = MATE_CP_BASE) -> float:
    """Fold a mate distance into the centi-pawn scale.

    "Mated in N" (``mate < 0``, and ``mate == 0``, which the engine uses for "already
    mated") -> ``-(mate_cp_base - N)``; "mate in N" (``mate > 0``) -> ``mate_cp_base - N``.
    """
    value = int(mate)
    distance = abs(value)
    if value > 0:
        return float(mate_cp_base - distance)
    return float(-mate_cp_base + distance)


def cp_from_mate(mate: int, *, mate_cp_base: int = MATE_CP_BASE) -> tuple[float, int | None]:
    """Return ``(cp, mate)`` for a mate score: the folded centi-pawns and the raw mate.

    Kept as a separate helper so the raw mate distance survives into reports next to the
    centi-pawn value it was folded into.
    """
    return mate_to_cp(mate, mate_cp_base=mate_cp_base), int(mate)


def score_to_cp(score: chess.engine.Score, *, mate_cp_base: int = MATE_CP_BASE) -> float | None:
    """Convert a :class:`chess.engine.Score` (``Cp``, ``Mate`` or ``MateGiven``) to cp.

    ``MateGiven`` -- python-chess's marker for "the side to move is already delivering
    mate", whose ``mate()`` is indistinguishable from ``Mate(0)`` -- maps to
    ``+mate_cp_base``, whereas ``Mate(0)`` ("the side to move is mated") maps to
    ``-mate_cp_base``.

    :returns: ``None`` only for a score type with neither a cp value nor a mate distance.
    """
    if isinstance(score, chess.engine.MateGivenType):
        return float(mate_cp_base)
    mate = score.mate()
    if mate is None:
        cp = score.score()
        return None if cp is None else float(cp)
    return mate_to_cp(mate, mate_cp_base=mate_cp_base)


def to_mover_perspective(score: chess.engine.PovScore, mover: chess.Color) -> chess.engine.PovScore:
    """Return ``score`` from the point of view of ``mover``. **The single conversion.**

    :param score: a score as reported by the engine, i.e. relative to the side to move of
        the analysed position.
    :param mover: the colour whose point of view we want. For the position *before* a
        move this is ``board_before.turn``; for the position *after* the move it is the
        same player again (the side to move has changed, the player has not).
    """
    if not isinstance(score, chess.engine.PovScore):
        raise TypeError(f"expected a PovScore from the engine, got {type(score).__name__}")
    return chess.engine.PovScore(score.pov(mover), mover)


def pov_to_mover_cp(
    score: chess.engine.PovScore,
    mover: chess.Color,
    *,
    mate_cp_base: int = MATE_CP_BASE,
) -> tuple[float | None, int | None]:
    """Convert an engine score to ``(cp_in_mover_pov, mate_in_mover_pov)``.

    ``cp`` is ``None`` only for ``MateGiven``; ``mate`` is ``None`` for ordinary
    centi-pawn scores.
    """
    mover_score = to_mover_perspective(score, mover)
    relative = mover_score.relative
    mate = relative.mate()
    if mate is None:
        cp = relative.score()
        return (None if cp is None else float(cp)), None
    return mate_to_cp(mate, mate_cp_base=mate_cp_base), int(mate)


def line_to_mover_perspective(line: LineInfo, mover: chess.Color) -> LineInfo:
    """Return ``line`` with all scores relative to ``mover`` (see :func:`to_mover_perspective`)."""
    if line.turn == mover:
        return line.model_copy()
    return line.model_copy(
        update={
            "turn": mover,
            "score_cp": None if line.score_cp is None else -float(line.score_cp),
            "mate": None if line.mate is None else -int(line.mate),
        }
    )


def lines_to_mover_perspective(lines: Sequence[LineInfo], mover: chess.Color) -> list[LineInfo]:
    """Apply :func:`line_to_mover_perspective` to every line."""
    return [line_to_mover_perspective(line, mover) for line in lines]


def best_line(lines: Sequence[LineInfo]) -> LineInfo | None:
    """Return the highest-ranked *unbounded* line, or ``None`` for an empty input.

    Aspiration-window bounds are skipped: a lower-bound line is optimistic, so using it
    as "the best move" would inflate every quality label.
    """
    for line in sorted(lines, key=lambda ln: ln.multipv_rank):
        if line.bound != "lower":
            return line
    return None


def line_eval_cp(line: LineInfo, *, mate_cp_base: int = MATE_CP_BASE) -> float:
    """The line's evaluation in centi-pawns, with mate scores folded in.

    ``LineInfo`` keeps mate scores in :attr:`~moveexp.schema.LineInfo.mate` and leaves
    :attr:`~moveexp.schema.LineInfo.score_cp` empty, so *every* consumer of a line's
    centi-pawn value must go through this function. A line with neither value scores
    ``0.0`` (it should not exist: ``StockfishClient`` drops unscored lines).
    """
    if line.score_cp is not None:
        return float(line.score_cp)
    if line.mate is not None:
        return mate_to_cp(line.mate, mate_cp_base=mate_cp_base)
    return 0.0


def win_prob_gap_to_second(lines: Sequence[LineInfo]) -> float:
    """Gap between the best and the second-best line by win probability.

    The two best lines are found by *value*, not by MultiPV rank: MultiPV ranks are only
    ordered from the point of view of the side to move, so after a perspective flip the
    rank order reverses.
    """
    probs = sorted(win_probs(lines), reverse=True)
    if len(probs) < 2:
        return 0.0
    return max(0.0, probs[0] - probs[1])


def find_rank(lines: Sequence[LineInfo], move_uci: str) -> int | None:
    """1-based MultiPV rank of ``move_uci`` within ``lines``, or ``None`` if absent."""
    for line in lines:
        if line.move == move_uci:
            return line.multipv_rank
    return None


def line_win_prob(
    line: LineInfo,
    *,
    scale: float = WIN_PROB_CP_SCALE,
    clamp: float = WIN_PROB_CP_CLAMP,
) -> float:
    """Win probability of a single line, in that line's own point of view.

    A forced mate is a certainty, so it short-circuits to ``1.0``/``0.0`` instead of being
    folded into centi-pawns and clamped (``mate_to_cp`` maps mate-in-``n`` to
    ``MATE_CP_BASE - n``, and the logistic only reaches ``0.996`` at the clamp). Unknown
    lines score ``0.5``, which makes every downstream "how good is this move" number come
    out neutral instead of silently claiming an advantage.
    """
    if line.score_cp is not None:
        return cp_to_win_prob(line.score_cp, scale=scale, clamp=clamp)
    if line.mate is not None:
        return 1.0 if line.mate > 0 else 0.0
    return 0.5


def win_probs(lines: Sequence[LineInfo]) -> list[float]:
    """Win probabilities of ``lines``, ordered by MultiPV rank.

    A line with no centi-pawn score (``None``) is treated as a forced mate: ``1.0`` when
    ``mate`` is positive for that line's own side, ``0.0`` when negative, ``0.5`` when
    unknown.
    """
    return [line_win_prob(line) for line in sorted(lines, key=lambda ln: ln.multipv_rank)]


#: Probability difference below which two float win probabilities count as equal. Used by
#: tests and by the audit tooling when it compares puzzle tags with detector output.
WIN_PROB_EPSILON: Final[float] = 1e-9
