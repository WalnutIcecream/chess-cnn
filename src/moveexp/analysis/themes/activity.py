"""Activity detectors (the ``activity`` themes).

These read where the mover's pieces stand after the move, plus a couple of simple counts.
They are geometric and never engine-backed:

* ``outpost`` -- the moved minor piece lands on an outpost;
* ``rook_open_file`` / ``rook_semi_open_file`` -- the moved rook lands on an open / semi-open
  file;
* ``rook_seventh`` -- the moved rook lands on the opponent's second rank;
* ``bishop_pair`` -- the mover owns both bishops;
* ``bad_bishop`` -- a mover bishop has no square it can step to (boxed in by its own pawns);
* ``develops_piece`` -- a minor piece or rook leaves the back rank and advances;
* ``controls_center`` -- the move increases central control (the ``space`` feature).
"""

from __future__ import annotations

import chess

from ...config import ROOK_SEVENTH_RANKS
from ..features import is_outpost
from .base import DetectionContext, ThemeHit, detector

__all__ = [
    "detect_bad_bishop",
    "detect_bishop_pair",
    "detect_controls_center",
    "detect_develops_piece",
    "detect_outpost",
    "detect_rook_open_file",
    "detect_rook_semi_open_file",
    "detect_rook_seventh",
]

_EPS = 1e-9


def _open_file(board: chess.Board, square: chess.Square) -> bool:
    """The square's file holds no pawns at all."""
    return not bool(board.pawns & chess.BB_FILES[chess.square_file(square)])


def _semi_open_file(board: chess.Board, square: chess.Square, side: chess.Color) -> bool:
    """The square's file holds enemy pawns but no friendly pawns."""
    file_mask = chess.BB_FILES[chess.square_file(square)]
    return bool(board.pawns & board.occupied_co[not side] & file_mask) and not bool(
        board.pawns & board.occupied_co[side] & file_mask
    )


@detector
def detect_outpost(ctx: DetectionContext) -> ThemeHit | None:
    """The moved minor piece lands on an outpost."""
    piece = ctx.moved_piece
    if piece is None or piece.piece_type not in (chess.KNIGHT, chess.BISHOP):
        return None
    if not is_outpost(ctx.after, ctx.to_square):
        return None
    return ThemeHit(
        theme="outpost",
        squares=ctx.squares(ctx.to_square),
        pieces=ctx.pieces(ctx.after, ctx.to_square),
        evidence=f"{ctx.pieces(ctx.after, ctx.to_square)[0]} stands on an outpost",
    )


@detector
def detect_rook_open_file(ctx: DetectionContext) -> ThemeHit | None:
    """The moved rook lands on a file with no pawns."""
    piece = ctx.moved_piece
    if piece is None or piece.piece_type != chess.ROOK:
        return None
    if not _open_file(ctx.after, ctx.to_square):
        return None
    return ThemeHit(
        theme="rook_open_file",
        squares=ctx.squares(ctx.to_square),
        pieces=ctx.pieces(ctx.after, ctx.to_square),
        evidence=(f"rook on the open {chess.FILE_NAMES[chess.square_file(ctx.to_square)]}-file"),
    )


@detector
def detect_rook_semi_open_file(ctx: DetectionContext) -> ThemeHit | None:
    """The moved rook lands on a file holding only enemy pawns."""
    piece = ctx.moved_piece
    if piece is None or piece.piece_type != chess.ROOK:
        return None
    if not _semi_open_file(ctx.after, ctx.to_square, ctx.side):
        return None
    return ThemeHit(
        theme="rook_semi_open_file",
        squares=ctx.squares(ctx.to_square),
        pieces=ctx.pieces(ctx.after, ctx.to_square),
        evidence=(
            f"rook on the semi-open {chess.FILE_NAMES[chess.square_file(ctx.to_square)]}-file"
        ),
    )


@detector
def detect_rook_seventh(ctx: DetectionContext) -> ThemeHit | None:
    """The moved rook lands on the opponent's second rank (the 'seventh')."""
    piece = ctx.moved_piece
    if piece is None or piece.piece_type != chess.ROOK:
        return None
    expected = ROOK_SEVENTH_RANKS[0] if ctx.side == chess.WHITE else ROOK_SEVENTH_RANKS[1]
    if chess.square_rank(ctx.to_square) != expected:
        return None
    return ThemeHit(
        theme="rook_seventh",
        squares=ctx.squares(ctx.to_square),
        pieces=ctx.pieces(ctx.after, ctx.to_square),
        evidence=f"rook reaches the seventh rank on {chess.square_name(ctx.to_square)}",
    )


@detector
def detect_bishop_pair(ctx: DetectionContext) -> ThemeHit | None:
    """The mover owns both bishops after the move."""
    bishops = [
        sq
        for sq, piece in ctx.after.piece_map().items()
        if piece.color == ctx.side and piece.piece_type == chess.BISHOP
    ]
    if len({(chess.square_file(sq) + chess.square_rank(sq)) % 2 for sq in bishops}) < 2:
        return None
    first, second = sorted(bishops)[:2]
    return ThemeHit(
        theme="bishop_pair",
        squares=ctx.squares(first, second),
        pieces=ctx.pieces(ctx.after, first, second),
        evidence="the mover owns both bishops",
    )


@detector
def detect_bad_bishop(ctx: DetectionContext) -> ThemeHit | None:
    """A mover bishop has no square it can step to (boxed in by its own pawns)."""
    for square, piece in ctx.after.piece_map().items():
        if piece.color != ctx.side or piece.piece_type != chess.BISHOP:
            continue
        # A bishop is bad when every square it attacks is its own piece: it is a tall pawn.
        if any(
            (target := ctx.after.piece_at(attacked)) is None or target.color != ctx.side
            for attacked in ctx.after.attacks(square)
        ):
            continue
        return ThemeHit(
            theme="bad_bishop",
            confidence=0.7,
            squares=ctx.squares(square),
            pieces=ctx.pieces(ctx.after, square),
            evidence=f"bishop on {chess.square_name(square)} is blocked by its own pawns",
        )
    return None


@detector
def detect_develops_piece(ctx: DetectionContext) -> ThemeHit | None:
    """A minor piece or rook leaves the back rank and advances."""
    piece = ctx.moved_piece
    if piece is None or piece.piece_type in (chess.PAWN, chess.KING, chess.QUEEN):
        return None
    home_rank = 0 if ctx.side == chess.WHITE else 7
    from_rank = chess.square_rank(ctx.from_square)
    to_rank = chess.square_rank(ctx.to_square)
    advanced = to_rank > from_rank if ctx.side == chess.WHITE else to_rank < from_rank
    if from_rank != home_rank or not advanced:
        return None
    return ThemeHit(
        theme="develops_piece",
        squares=ctx.squares(ctx.from_square, ctx.to_square),
        pieces=ctx.pieces(ctx.after, ctx.to_square),
        evidence=f"{ctx.pieces(ctx.after, ctx.to_square)[0]} develops off the back rank",
    )


@detector
def detect_controls_center(ctx: DetectionContext) -> ThemeHit | None:
    """The move increases the mover's control of the centre (the ``space`` feature)."""
    before = ctx.features_before.space
    after = ctx.features_after.space
    if after <= before + _EPS:
        return None
    return ThemeHit(
        theme="controls_center",
        confidence=0.8,
        evidence=f"central control rises from {before:.2f} to {after:.2f}",
    )
