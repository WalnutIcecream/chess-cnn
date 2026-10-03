"""Material detectors (the ``material`` themes).

These are inexpensive: they read the SEE result, the move type and simple counts. A single
capture can legitimately carry several of these at once (a capture that is also a trade that
simplifies); the registry keeps all of them because they are different themes.

The definition of a *sacrifice* here is deliberately conservative and **static**: the move
must give up a worthwhile piece by SEE (a queen for a pawn, a rook for a minor, ...). Whether
that sacrifice is *correct* -- whether the engine evaluation holds or improves, so it is not
simply a blunder -- is a quality-layer decision (:func:`moveexp.analysis.move_quality.classify_special`),
not a geometric one, and lives outside this module.
"""

from __future__ import annotations

import chess

from ...config import (
    PROMOTION_THREAT_RANKS,
    SACRIFICE_MARGIN_CP,
    SACRIFICE_MIN_PIECE_CP,
)
from ..features import is_passed_pawn
from ..see import piece_value_cp
from .base import DetectionContext, ThemeHit, detector

__all__ = [
    "detect_capture",
    "detect_promotion",
    "detect_promotion_threat",
    "detect_sacrifice",
    "detect_simplification",
    "detect_trade",
]


@detector
def detect_capture(ctx: DetectionContext) -> ThemeHit | None:
    """Material taken by the move."""
    if not ctx.is_capture:
        return None
    target = ctx.captured
    if target is None:
        return None
    return ThemeHit(
        theme="capture",
        squares=ctx.squares(ctx.from_square, ctx.to_square),
        pieces=ctx.pieces(ctx.after, ctx.to_square),
        evidence=f"takes the {ctx.pieces(ctx.board, ctx.to_square)[0]}",
    )


@detector
def detect_sacrifice(ctx: DetectionContext) -> ThemeHit | None:
    """A capture that gives up a more valuable piece than it takes, by SEE.

    A capture that wins material outright (``gain > margin``) is a capture/trade, not a
    sacrifice; a sacrifice *loses* the exchange. Whether it is a good sacrifice is the
    quality layer's job.
    """
    if not ctx.is_capture:
        return None
    gain = ctx.see.gain_cp
    if gain > SACRIFICE_MARGIN_CP:
        return None
    moved = ctx.moved_piece
    target = ctx.captured
    if moved is None or target is None:
        return None
    moved_value = piece_value_cp(moved.piece_type)
    target_value = piece_value_cp(target.piece_type)
    if moved_value <= target_value + SACRIFICE_MARGIN_CP:
        return None
    if moved_value < SACRIFICE_MIN_PIECE_CP:
        return None
    return ThemeHit(
        theme="sacrifice",
        confidence=0.8,
        squares=ctx.squares(ctx.from_square, ctx.to_square),
        pieces=ctx.pieces(ctx.after, ctx.to_square),
        evidence=(
            f"gives up the {ctx.pieces(ctx.board, ctx.from_square)[0]} for the "
            f"{ctx.pieces(ctx.board, ctx.to_square)[0]}"
        ),
    )


@detector
def detect_trade(ctx: DetectionContext) -> ThemeHit | None:
    """Roughly even exchange of material (any non-zero pieces, pawns included)."""
    if not ctx.is_capture:
        return None
    if ctx.see.gain_cp < -SACRIFICE_MARGIN_CP or ctx.see.gain_cp > SACRIFICE_MARGIN_CP:
        return None
    moved = ctx.moved_piece
    target = ctx.captured
    if moved is None or target is None:
        return None
    moved_value = piece_value_cp(moved.piece_type)
    target_value = piece_value_cp(target.piece_type)
    if moved_value == 0 or target_value == 0:
        return None
    if abs(moved_value - target_value) <= SACRIFICE_MARGIN_CP:
        return ThemeHit(
            theme="trade",
            confidence=0.8,
            squares=ctx.squares(ctx.from_square, ctx.to_square),
            pieces=ctx.pieces(ctx.after, ctx.to_square),
            evidence=(
                f"trades the {ctx.pieces(ctx.board, ctx.from_square)[0]} for the "
                f"{ctx.pieces(ctx.board, ctx.to_square)[0]}"
            ),
        )
    return None


@detector
def detect_simplification(ctx: DetectionContext) -> ThemeHit | None:
    """An even exchange of worthwhile pieces (minor or better), thinning the board.

    Distinct from :func:`detect_trade`: a pawn-for-pawn swap is a trade but not a
    simplification -- only exchanges of at least a minor each reduce the position's
    complexity, which is what "simplification" means here.
    """
    if not ctx.is_capture:
        return None
    gain = ctx.see.gain_cp
    if gain < -SACRIFICE_MARGIN_CP or gain > SACRIFICE_MARGIN_CP:
        return None
    moved = ctx.moved_piece
    target = ctx.captured
    if moved is None or target is None:
        return None
    moved_value = piece_value_cp(moved.piece_type)
    target_value = piece_value_cp(target.piece_type)
    if moved_value < SACRIFICE_MIN_PIECE_CP or target_value < SACRIFICE_MIN_PIECE_CP:
        return None
    return ThemeHit(
        theme="simplification",
        confidence=0.8,
        squares=ctx.squares(ctx.from_square, ctx.to_square),
        pieces=ctx.pieces(ctx.after, ctx.to_square),
        evidence=(
            f"trades the {ctx.pieces(ctx.board, ctx.from_square)[0]} for the "
            f"{ctx.pieces(ctx.board, ctx.to_square)[0]} and thins the board"
        ),
    )


@detector
def detect_promotion(ctx: DetectionContext) -> ThemeHit | None:
    """The move promotes."""
    if not ctx.is_promotion:
        return None
    piece_after = ctx.moved_piece_after
    kind = piece_after.symbol() if piece_after else "?"
    return ThemeHit(
        theme="promotion",
        squares=ctx.squares(ctx.from_square, ctx.to_square),
        pieces=ctx.pieces(ctx.after, ctx.to_square),
        evidence=f"promotes to {kind}",
    )


@detector
def detect_promotion_threat(ctx: DetectionContext) -> ThemeHit | None:
    """Leaves a passed pawn within :data:`~moveexp.config.PROMOTION_THREAT_RANKS` of promoting."""
    promotion_rank = 7 if ctx.side == chess.WHITE else 0
    for square in chess.SquareSet(ctx.after.pawns & ctx.after.occupied_co[ctx.side]):
        rank = chess.square_rank(square)
        steps = promotion_rank - rank if ctx.side == chess.WHITE else rank - promotion_rank
        if not 0 < steps <= PROMOTION_THREAT_RANKS:
            continue
        if is_passed_pawn(ctx.after, square, ctx.side):
            return ThemeHit(
                theme="promotion_threat",
                confidence=0.8,
                squares=ctx.squares(square),
                pieces=ctx.pieces(ctx.after, square),
                evidence=(
                    f"passed pawn on {chess.square_name(square)} is {steps} step(s) from promoting"
                ),
            )
    return None
