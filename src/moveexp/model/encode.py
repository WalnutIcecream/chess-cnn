"""Board-tensor encoding for the neural baseline (numpy + python-chess only).

The encoding is deliberately simple and stateless so it can be tested without torch:
12 piece planes (one per ``PNBRQK`` in each colour), one side-to-move plane, and two
planes marking the played move's from/to squares. Stacked in CHW order, row 0 is rank 8.
"""

from __future__ import annotations

import chess
import numpy as np

#: Plane order: white pieces then black pieces.
PIECE_PLANES: tuple[str, ...] = ("P", "N", "B", "R", "Q", "K", "p", "n", "b", "r", "q", "k")
#: Number of piece-placement planes.
N_PIECES: int = len(PIECE_PLANES)
#: Total planes: pieces + side-to-move + from-square + to-square.
N_PLANES: int = N_PIECES + 3


def _square_to_rc(square: chess.Square) -> tuple[int, int]:
    """Board square to ``(row, col)`` with rank 8 in row 0."""
    return 7 - chess.square_rank(square), chess.square_file(square)


def encode_board(fen: str, move_uci: str | None = None) -> np.ndarray:
    """Encode a position (and optionally a move) as a ``(N_PLANES, 8, 8)`` float array."""
    board = chess.Board(fen)
    planes = np.zeros((N_PLANES, 8, 8), dtype=np.float32)

    for square, piece in board.piece_map().items():
        row, col = _square_to_rc(square)
        planes[PIECE_PLANES.index(piece.symbol()), row, col] = 1.0

    if board.turn == chess.WHITE:
        planes[N_PIECES, :, :] = 1.0

    if move_uci:
        try:
            move = chess.Move.from_uci(move_uci)
        except ValueError:
            move = None
        if move is not None:
            row, col = _square_to_rc(move.from_square)
            planes[N_PIECES + 1, row, col] = 1.0
            row, col = _square_to_rc(move.to_square)
            planes[N_PIECES + 2, row, col] = 1.0

    return planes


def n_planes(use_move: bool) -> int:
    """Channel count for an encoder call: 15 with the move planes, 13 without."""
    return N_PLANES if use_move else N_PIECES + 1


# --------------------------------------------------------------------------------------
# Symmetry augmentation
# --------------------------------------------------------------------------------------
# The board admits two label-preserving symmetries: reflecting it left-to-right (files
# reversed) and swapping the colours (which must be combined with a 180-degree rotation to
# map the position onto itself). Both leave the mover's-point-of-view evaluation and every
# theme/intent label unchanged, so they are free training data. These helpers work on a single
# ``(C, 8, 8)`` array or a whole ``(N, C, 8, 8)`` batch: the leading axes are handled with
# ellipsis, so the same call is used per-sample and per-batch.


def colour_flip(planes: np.ndarray) -> np.ndarray:
    """Swap white and black and rotate the board 180 degrees (a board symmetry).

    A bare colour swap is not a symmetry -- it would send a white pawn on e2 to a black pawn
    on e2, where pawns move the other way. Rotating as well sends it to e7, which is the same
    position seen from the other side and has identical labels.
    """
    out = np.empty_like(planes)
    half = N_PIECES // 2  # six piece types per colour
    pieces = planes[..., :N_PIECES, :, :]
    out[..., :half, :, :] = pieces[..., half:, :, :][..., ::-1, ::-1]
    out[..., half:N_PIECES, :, :] = pieces[..., :half, :, :][..., ::-1, ::-1]
    out[..., N_PIECES, :, :] = 1.0 - planes[..., N_PIECES, :, :]
    out[..., N_PIECES + 1 :, :, :] = planes[..., N_PIECES + 1 :, :, :][..., ::-1, ::-1]
    return out


def mirror_files(planes: np.ndarray) -> np.ndarray:
    """Reflect the board left-to-right: the a-file becomes the h-file (a board symmetry)."""
    return planes[..., ::-1].copy()


def augment_planes(
    planes: np.ndarray, *, mirror: bool = False, switch_colour: bool = False
) -> np.ndarray:
    """Apply the requested label-preserving symmetries to ``planes`` (single or batch)."""
    out = colour_flip(planes) if switch_colour else planes
    return mirror_files(out) if mirror else out
