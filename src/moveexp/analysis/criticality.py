"""Criticality: did this move matter, and was anything else available?

Criticality answers a different question from move quality. Quality is "did you play a
reasonable move"; criticality is "did this position have a single sensible continuation,
or was the move a bolt from the blue". A quiet improving move in an equal position is a
good move and a non-critical one; a forced recapture in a sharp position can be excellent
and highly critical.

Everything here works on the mover's point of view and in win probability, because a
centi-pawn gap of 300 means "fine" at one point of the game and "critical" in another.

Fields produced:

``gap_to_second_wp``
    ``P(win | best move) - P(win | second best move)``. Large gaps mean the engine found
    only one move worth playing -- the formal version of "the only move".
``is_only_move``
    ``gap_to_second_wp`` above :data:`moveexp.config.ONLY_MOVE_GAP_WP`.
``sharpness``
    Spread of win probability *across all MultiPV lines* (max - min). High sharpness means
    the position has several very different continuations, i.e. tactics are flying.
``is_forcing``
    The move is a check, a capture, or the PV it found is a forced mate. Forcing moves
    rarely need "intent" language: they are simply the only moves.
``is_critical``
    ``is_only_move`` **or** ``sharpness`` above threshold **or** the played move changed
    the win probability by more than :data:`moveexp.config.CRITICAL_WIN_PROB_CHANGE`.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import chess

from ..config import (
    CRITICAL_SHARPNESS,
    CRITICAL_WIN_PROB_CHANGE,
    FORCING_MATE_MAX_UNITS,
    ONLY_MOVE_GAP_WP,
)
from ..engine.eval_utils import (
    best_line,
    lines_to_mover_perspective,
    win_prob_gap_to_second,
    win_probs,
)

__all__ = [
    "Criticality",
    "assess_criticality",
    "gap_to_second_wp",
    "is_forcing",
    "sharpness",
]


@dataclass(frozen=True)
class Criticality:
    """Criticality signals for one move. All win probabilities are mover-perspective."""

    gap_to_second_wp: float
    is_only_move: bool
    sharpness: float
    is_forcing: bool
    is_critical: bool
    n_lines: int
    forcing_reason: str = ""
    """Which condition triggered ``is_forcing`` -- useful in audits and prompts."""

    def to_dict(self) -> dict[str, Any]:
        """JSON-friendly dict."""
        return {
            "gap_to_second_wp": self.gap_to_second_wp,
            "is_only_move": self.is_only_move,
            "sharpness": self.sharpness,
            "is_forcing": self.is_forcing,
            "is_critical": self.is_critical,
            "n_lines": self.n_lines,
            "forcing_reason": self.forcing_reason,
        }


def gap_to_second_wp(lines: Sequence[Any], *, mover: chess.Color | None = None) -> float:
    """Win-probability gap between the best and the second-best line.

    :param lines: engine lines; scores relative to their own ``turn``.
    :param mover: point of view to convert to. Defaults to the first line's own point of
        view (i.e. no conversion), which is correct when the lines come from a position
        where the mover was to move.
    :returns: ``0.0`` when fewer than two usable lines were returned -- the engine stopped
        early, so "no second best" must not be read as "the only move".
    """
    return win_prob_gap_to_second(_usable(lines, mover))


def sharpness(lines: Sequence[Any], *, mover: chess.Color | None = None) -> float:
    """Spread of win probability across the MultiPV set (``max - min``)."""
    usable = _usable(lines, mover)
    probs = win_probs(usable)
    if len(probs) < 2:
        return 0.0
    return max(probs) - min(probs)


def is_forcing(
    board_before: chess.Board,
    move: chess.Move,
    board_after: chess.Board,
    lines: Sequence[Any] | None = None,
    *,
    mover: chess.Color | None = None,
    max_mate_units: int = FORCING_MATE_MAX_UNITS,
) -> tuple[bool, str]:
    """Whether the move is forcing, plus the reason.

    A move counts as forcing when any of the following holds:

    * it gives check (``board_after.is_check()``; python-chess only offers a *position*
      level ``gives_check()``, so the check is tested on the resulting position),
    * it captures (``board_before.is_capture(move)``, which covers en passant),
    * the best PV line is a forced mate within ``max_mate_units``.

    :returns: ``(is_forcing, reason)`` where ``reason`` is an empty string when not
        forcing. The reason is stored in reports and shown to the user instead of a bare
        boolean.
    """
    if board_after.is_check():
        return True, "the move gives check"
    if board_before.is_capture(move):
        return True, "the move captures a piece"
    if lines:
        top = best_line(_usable(lines, mover if mover is not None else board_before.turn))
        if top is not None and top.mate is not None and abs(top.mate) <= max_mate_units:
            side = "mates" if top.mate > 0 else "is mated"
            return True, f"the engine line {side} in {abs(top.mate)}"
    return False, ""


def assess_criticality(
    board_before: chess.Board,
    move: chess.Move,
    board_after: chess.Board,
    lines_before: Sequence[Any],
    *,
    win_prob_before: float,
    win_prob_after: float,
    only_move_gap_wp: float = ONLY_MOVE_GAP_WP,
    critical_sharpness: float = CRITICAL_SHARPNESS,
    critical_wp_change: float = CRITICAL_WIN_PROB_CHANGE,
) -> Criticality:
    """Combine all criticality signals for one move.

    :param lines_before: MultiPV lines of the position before the move (any point of view;
        they are converted to ``board_before.turn`` internally).
    :param win_prob_before: win probability of the position before the move, mover POV.
    :param win_prob_after: win probability after the move, mover POV.
    """
    mover = board_before.turn
    usable = _usable(lines_before, mover)
    probs = win_probs(usable)
    gap = win_prob_gap_to_second(usable)
    spread = (max(probs) - min(probs)) if len(probs) > 1 else 0.0
    only_move = gap > only_move_gap_wp
    forcing, reason = is_forcing(board_before, move, board_after, usable, mover=mover)
    wp_change = abs(win_prob_after - win_prob_before)
    critical = only_move or spread >= critical_sharpness or wp_change >= critical_wp_change
    return Criticality(
        gap_to_second_wp=gap,
        is_only_move=only_move,
        sharpness=spread,
        is_forcing=forcing,
        is_critical=bool(critical),
        n_lines=len(usable),
        forcing_reason=reason,
    )


def _usable(lines: Sequence[Any], mover: chess.Color | None) -> list[Any]:
    """Drop lower-bound lines and convert the survivors to ``mover``'s point of view."""
    kept = [line for line in lines if line.bound != "lower"]
    if mover is None:
        return kept
    return lines_to_mover_perspective(kept, mover)
