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
