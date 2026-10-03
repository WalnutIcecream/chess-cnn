"""Positions for the SEE and detector tests, built piece by piece.

Hand-written FENs are a reliable source of silent mistakes (lowercase means *black*, and
an easy FEN is usually an impossible one: two kings facing each other down an empty file).
:func:`board` therefore places pieces explicitly and refuses to hand back a position that
python-chess considers illegal, which makes a broken fixture fail loudly instead of
quietly testing the wrong thing.
"""

from __future__ import annotations

import chess


def board(
    *pieces: str,
    turn: chess.Color = chess.WHITE,
    castling: str = "-",
    ep: str | None = None,
) -> chess.Board:
    """Build a position from ``"wR@e1"`` / ``"bQ@d8"`` style specifications.

    :param pieces: alternating colour (``w``/``b``), piece letter and ``@square``.
    :param turn: side to move.
    :param castling: castling rights in FEN notation.
    :param ep: en-passant target square, e.g. ``"d6"``.
    :raises ValueError: if the resulting position is not legal.
    """
    b = chess.Board(None, castling_rights=castling) if castling != "-" else chess.Board(None)
    for spec in pieces:
        colour = chess.WHITE if spec[0] == "w" else chess.BLACK
        letter = spec[1].upper()
        piece_type = {
            "P": chess.PAWN,
            "N": chess.KNIGHT,
            "B": chess.BISHOP,
            "R": chess.ROOK,
            "Q": chess.QUEEN,
            "K": chess.KING,
        }[letter]
        square = chess.parse_square(spec.split("@")[1])
        b.set_piece_at(square, chess.Piece(piece_type, colour))
    b.turn = turn
    b.ep_square = chess.parse_square(ep) if ep else None
    if b.status() != chess.STATUS_VALID:
        raise ValueError(f"fixture is not a legal position: {b.status()!r} in {b.fen()}")
    return b


def after(*sans: str) -> chess.Board:
    """Play a real sequence of SAN moves from the initial position."""
    b = chess.Board()
    for san in sans:
        b.push_san(san)
    return b
