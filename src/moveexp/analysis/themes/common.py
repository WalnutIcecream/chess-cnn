"""Shared vocabulary for the detectors: who attacks what, and what it is worth.

Detectors in this package all ask the same three questions -- "is this square attacked",
"by whom, and by how many", and "what is that piece worth" -- and all of them must answer
them the same way, otherwise two detectors can contradict each other in the same report. The
answers therefore live here once.

Counting rules, applied everywhere:

* **Kings are attackers, not captures.** A king one step away from a piece matters (it
  defends, it pins by proximity), but "king takes rook" is not an exchange -- that is why
  :mod:`moveexp.analysis.see` leaves kings out of the exchange sequences and these helpers
  count them only where the question is about attacks and defences.
* **A "net attacker" is a number, not a yes/no.** ``attackers - defenders`` distinguishes a
  piece hanging loose (1) from a piece under real pressure (-1), which is what separates a
  free capture from a defended threat.
* **Values come from the config table**, never from the engine, so an explanation can be
  checked by hand.
"""

from __future__ import annotations

import chess

from ...config import PIECE_VALUE_CP

__all__ = [
    "attacker_count",
    "defender_count",
    "defensive_count",
    "is_attacked_by",
    "king_value_cp",
    "net_attackers",
    "occupied_attackers",
    "piece_value",
    "value_at",
]

#: Value credited to the king when it is the *target* of an attack. A fork that also hits the
#: king is the most valuable fork there is, and giving the king 0cp would let every fork on
#: the king look like a fork on a pawn.
king_value_cp = PIECE_VALUE_CP["q"]


def piece_value(piece: chess.Piece | None) -> int:
    """Centi-pawn value of a piece; ``0`` for an empty square and for kings."""
    if piece is None or piece.piece_type == chess.KING:
        return 0
    return PIECE_VALUE_CP[piece.symbol().lower()]


def value_at(board: chess.Board, square: chess.Square) -> int:
    """Centi-pawn value standing on ``square`` (see :func:`king_value_cp` for kings)."""
    return piece_value(board.piece_at(square))


def attacker_count(board: chess.Board, square: chess.Square, side: chess.Color) -> int:
    """How many pieces of ``side`` attack ``square``."""
    return (board.attackers_mask(side, square) & board.occupied_co[side]).bit_count()


def defender_count(board: chess.Board, square: chess.Square, side: chess.Color) -> int:
    """How many pieces of ``side`` defend ``square``."""
    return attacker_count(board, square, not side)


def net_attackers(board: chess.Board, square: chess.Square, side: chess.Color) -> int:
    """``side``'s attackers minus the opponent's defenders.

    Positive means ``side`` wins the piece if the opponent does nothing; ``1`` is the
    classic hanging piece; ``0`` is an even fight over material.
    """
    return attacker_count(board, square, side) - defender_count(board, square, side)


def is_attacked_by(board: chess.Board, square: chess.Square, side: chess.Color) -> bool:
    """Does any piece of ``side`` attack ``square``?"""
    return bool(board.attackers_mask(side, square) & board.occupied_co[side])


def occupied_attackers(
    board: chess.Board,
    square: chess.Square,
    side: chess.Color,
    *,
    include_kings: bool = True,
) -> list[chess.Square]:
    """Squares of the pieces of ``side`` that attack ``square``.

    Returned as squares (not pieces) because a detector almost always wants to say
    ``"N@f3"`` in its evidence, and a list of pieces cannot produce that.
    """
    attackers = board.attackers_mask(side, square) & board.occupied_co[side]
    if not include_kings:
        attackers &= ~board.kings
    return [square for square in chess.SquareSet(attackers)]


def defensive_count(board: chess.Board, side: chess.Color, *, include_kings: bool = True) -> int:
    """Number of pieces of ``side`` that defend something else (used for the "naked king" themes)."""
    mask = board.occupied_co[side]
    if not include_kings:
        mask &= ~board.kings
    return mask.bit_count()
