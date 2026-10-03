"""Move quality: how much win probability did the move cost?

The whole module works in the **mover's point of view**: every evaluation is positive
when the position is good for the player who played the move. The conversion from the
engine's side-to-move scores happens exactly once, in
:func:`moveexp.engine.eval_utils.lines_to_mover_perspective`.

Label bands (``config.QUALITY_LOSS_WP_THRESHOLDS``) operate on ``loss_wp``, the drop in
win probability relative to the engine's best move:

======  ====================  ==================================================
label   ``loss_wp`` band     meaning
======  ====================  ==================================================
best    rank 1 or < 0.005     indistinguishable from the engine's choice
exc.    < 0.02               playable
good    < 0.05               imprecise
inacc.  < 0.10               clearly inferior
mistake < 0.20               gives away a big chunk of the advantage
blunder >= 0.20              throws the game away
======  ====================  ==================================================

``great`` and ``brilliant`` are *not* decided here: they need extra evidence (is this the
only good move? is the sacrifice confirmed by the engine?) so they live in
:func:`classify_special`, which the pipeline calls afterwards.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from typing import Any

import chess

from ..config import (
    BRILLIANT_WIN_PROB_CEILING,
    GREAT_WIN_PROB_SWING,
    QUALITY_BEST_RANK,
    QUALITY_LOSS_WP_THRESHOLDS,
)
from ..engine.eval_utils import (
    best_line,
    find_rank,
    line_eval_cp,
    line_win_prob,
    lines_to_mover_perspective,
    win_probs,
)
from ..schema import LineInfo

__all__ = ["MoveQuality", "assess_move", "classify_loss", "classify_special"]

#: Labels walked in *increasing* severity of ``loss_wp``, i.e. the order in which
#: :func:`classify_loss` tests the thresholds (tightest bound first).
_LABEL_ORDER: tuple[str, ...] = (
    "best",
    "excellent",
    "good",
    "inaccuracy",
    "mistake",
    "blunder",
)


@dataclass(frozen=True)
class MoveQuality:
    """Move-quality numbers, all in the mover's point of view."""

    label: str
    eval_before_cp: float
    eval_after_cp: float
    win_prob_before: float
    win_prob_after: float
    loss_cp: float
    loss_wp: float
    best_move: str | None
    best_move_san: str | None
    best_move_cp: float
    best_move_wp: float
    rank: int | None
    n_lines: int
    played_in_multipv: bool

    def with_label(self, label: str) -> MoveQuality:
        """Return a copy with a different label (``great`` / ``brilliant`` overrides)."""
        return replace(self, label=label)

    def to_dict(self) -> dict[str, Any]:
        """JSON-friendly dict (the board is dropped)."""
        return {
            "label": self.label,
            "eval_before_cp": self.eval_before_cp,
            "eval_after_cp": self.eval_after_cp,
            "win_prob_before": self.win_prob_before,
            "win_prob_after": self.win_prob_after,
            "loss_cp": self.loss_cp,
            "loss_wp": self.loss_wp,
            "best_move": self.best_move,
            "best_move_san": self.best_move_san,
            "best_move_cp": self.best_move_cp,
            "best_move_wp": self.best_move_wp,
            "rank": self.rank,
            "n_lines": self.n_lines,
            "played_in_multipv": self.played_in_multipv,
        }


def classify_loss(
    loss_wp: float,
    *,
    rank: int | None = None,
    thresholds: Mapping[str, float] | None = None,
) -> str:
    """Map a win-probability loss to a quality label.

    :param loss_wp: ``max(0, win_prob_of_best - win_prob_of_played)``.
    :param rank: MultiPV rank of the played move. Rank 1 forces ``"best"`` regardless of
        ``loss_wp``: the engine prefers the move it was shown, so any loss is an artefact
        of the evaluation being computed from a deeper/parallel line.
    :param thresholds: override for :data:`moveexp.config.QUALITY_LOSS_WP_THRESHOLDS`.
    """
    bands = thresholds or QUALITY_LOSS_WP_THRESHOLDS
    if rank is not None and rank <= QUALITY_BEST_RANK:
        return "best"
    for label in _LABEL_ORDER:
        upper = bands.get(label)
        if upper is not None and loss_wp < upper:
            return label
    return _LABEL_ORDER[-2]  # unreachable with the default thresholds; degrade safely


def assess_move(
    board_before: chess.Board,
    move: chess.Move,
    lines_before: Sequence[LineInfo],
    lines_after: Sequence[LineInfo] | None = None,
    *,
    thresholds: Mapping[str, float] | None = None,
) -> MoveQuality:
    """Score the played ``move`` given MultiPV lines from before and after it.

    :param board_before: position before the move (never mutated).
    :param move: the played move; must be legal in ``board_before``.
    :param lines_before: MultiPV lines of ``board_before`` as returned by the engine, i.e.
        scores relative to ``board_before.turn``.
    :param lines_after: single-PV line(s) of the position after the move, scores relative
        to the *opponent*. Pass ``None`` only when the played move was among
        ``lines_before``, in which case its own line supplies ``eval_after``.
    :raises ValueError: if there are no usable lines, if the move is illegal, or if the
        evaluation of the resulting position is unknown.
    """
    if move not in board_before.legal_moves:
        raise ValueError(f"illegal move {move.uci()} in position {board_before.fen()}")

    mover = board_before.turn
    before = lines_to_mover_perspective(lines_before, mover)
    before = [line for line in before if line.bound != "lower"]
    best = best_line(before)
    if best is None:
        raise ValueError("no usable engine lines for the position before the move")

    best_cp = line_eval_cp(best)
    best_wp = line_win_prob(best)
    move_uci = move.uci()
    rank = find_rank(before, move_uci)
    played_in_multipv = rank is not None
    best_move_san = _to_san(board_before, best.move)

    if played_in_multipv:
        played = next(line for line in before if line.move == move_uci)
        eval_after = line_eval_cp(played)
        wp_after = line_win_prob(played)
    else:
        if not lines_after:
            raise ValueError(
                f"move {move_uci} is not in the MultiPV set and no after-search was provided"
            )
        after = lines_to_mover_perspective(lines_after, mover)
        after_best = best_line(after)
        if after_best is None:
            raise ValueError("no usable engine line for the position after the move")
        eval_after = line_eval_cp(after_best)
        wp_after = line_win_prob(after_best)

    wp_before = best_wp
    loss_cp = max(0.0, best_cp - eval_after)
    loss_wp = max(0.0, wp_before - wp_after)
    label = classify_loss(loss_wp, rank=rank, thresholds=thresholds)

    return MoveQuality(
        label=label,
        eval_before_cp=best_cp,
        eval_after_cp=eval_after,
        win_prob_before=wp_before,
        win_prob_after=wp_after,
        loss_cp=loss_cp,
        loss_wp=loss_wp,
        best_move=best.move,
        best_move_san=best_move_san,
        best_move_cp=best_cp,
        best_move_wp=best_wp,
        rank=rank,
        n_lines=len(before),
        played_in_multipv=played_in_multipv,
    )


def classify_special(
    quality: MoveQuality,
    board_before: chess.Board,
    move: chess.Move,
    lines_before: Sequence[LineInfo],
    *,
    sacrifice_confirmed: bool = False,
    great_win_prob_swing: float = GREAT_WIN_PROB_SWING,
    brilliant_wp_ceiling: float = BRILLIANT_WIN_PROB_CEILING,
) -> str | None:
    """Decide whether a ``best``/``excellent`` move deserves ``great`` or ``brilliant``.

    Both labels are *optional extras*: they are rare and easy to get wrong, so bulk
    labelling leaves them off by default, but they are cheap for the interactive CLI.

    ``great``
        Rank 1 **and** the win-probability swing between the best and the second-best line
        is at least ``great_win_prob_swing`` -- i.e. it is unmistakably the only good
        move. Only considered for moves already labelled ``best``.

    ``brilliant``
        ``best``/``excellent``/``great`` **and** ``sacrifice_confirmed`` (Stage 2 passes
        ``True`` only when SEE says material is given up *and* the engine evaluation holds
        or improves) **and** the move is not a plain recapture **and** the position before
        the move was not already winning (``win_prob_before < brilliant_wp_ceiling``):
        combining into a won position is not brilliant.

    :returns: ``"great"``, ``"brilliant"`` or ``None`` to keep the existing label.
    """
    mover = board_before.turn
    lines = [ln for ln in lines_to_mover_perspective(lines_before, mover) if ln.bound != "lower"]
    probs = win_probs(lines)
    swing = (probs[0] - probs[1]) if len(probs) > 1 else 0.0

    if quality.label == "best" and quality.rank == 1 and swing >= great_win_prob_swing:
        return "great"

    eligible = quality.label in ("best", "excellent", "great")
    is_recapture = board_before.is_capture(move)
    if (
        eligible
        and sacrifice_confirmed
        and not is_recapture
        and quality.win_prob_before < brilliant_wp_ceiling
    ):
        return "brilliant"
    return None


def _to_san(board: chess.Board, uci: str | None) -> str | None:
    """SAN for a UCI move in ``board``, or ``None`` if it is not a legal move there."""
    if not uci:
        return None
    try:
        move = board.parse_uci(uci)
    except ValueError:
        return None
    return board.san(move)
