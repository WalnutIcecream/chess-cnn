"""King-safety detectors (the ``king_safety`` themes).

These report *changes* in king safety caused by the move, for the mover and for the
opponent. The score itself comes from :func:`moveexp.analysis.features.snapshot`: own pawn
shield around the king minus enemy pressure on the king zone, so a positive change is a
safer king and a negative one is exposure.

Three themes cover the three directions of interest:

* ``exposes_king`` -- the mover's own king safety got worse;
* ``shelters_king`` -- the mover's own king safety got better;
* ``weakens_opponent_king`` -- the opponent's king safety got worse.

Each detector reports at most one hit and puts the size of the change in the evidence.
"""

from __future__ import annotations

import chess

from ..features import snapshot
from .base import DetectionContext, ThemeHit, detector

__all__ = ["detect_exposes_king", "detect_shelters_king", "detect_weakens_opponent_king"]

#: Any real change counts. King safety is a pawn count minus a pressure term, so its
#: smallest step (``KING_ATTACK_WEIGHT``) is far above float noise; this epsilon only
#: absorbs rounding.
_EPS = 1e-9


def _safety(board: chess.Board, side: chess.Color) -> float:
    return snapshot(board, side).king_safety


@detector
def detect_exposes_king(ctx: DetectionContext) -> ThemeHit | None:
    """The mover's own king safety got worse (shield lost or pressure added)."""
    before = ctx.features_before.king_safety
    after = ctx.features_after.king_safety
    if after >= before - _EPS:
        return None
    king = ctx.after.king(ctx.side)
    return ThemeHit(
        theme="exposes_king",
        squares=ctx.squares(king) if king is not None else (),
        pieces=ctx.pieces(ctx.after, king) if king is not None else (),
        evidence=f"king safety drops from {before:.2f} to {after:.2f}",
    )


@detector
def detect_shelters_king(ctx: DetectionContext) -> ThemeHit | None:
    """The mover's own king safety got better."""
    before = ctx.features_before.king_safety
    after = ctx.features_after.king_safety
    if after <= before + _EPS:
        return None
    king = ctx.after.king(ctx.side)
    return ThemeHit(
        theme="shelters_king",
        squares=ctx.squares(king) if king is not None else (),
        pieces=ctx.pieces(ctx.after, king) if king is not None else (),
        evidence=f"king safety rises from {before:.2f} to {after:.2f}",
    )


@detector
def detect_weakens_opponent_king(ctx: DetectionContext) -> ThemeHit | None:
    """The opponent's king safety got worse."""
    before = _safety(ctx.board, ctx.opponent)
    after = _safety(ctx.after, ctx.opponent)
    if after >= before - _EPS:
        return None
    king = ctx.after.king(ctx.opponent)
    return ThemeHit(
        theme="weakens_opponent_king",
        confidence=0.7,
        squares=ctx.squares(king) if king is not None else (),
        pieces=ctx.pieces(ctx.after, king) if king is not None else (),
        evidence=f"opponent king safety drops from {before:.2f} to {after:.2f}",
    )
