"""Pawn-structure detectors (the ``structure`` themes).

These compare the mover's pawn structure before and after the move. A plain theme
(``passed_pawn``, ``isolated_pawn``, ``doubled_pawn``, ``backward_pawn``) reports that the
mover *has* that feature after the move; the ``creates_*`` themes report that the move is
what produced the first instance of it -- operationally, the mover had none before and at
least one after. That is a deliberate simplification: adding a *second* passed pawn to a
position that already has one is not "creating a passed pawn", it is deepening an existing
one.

A ``pawn_break`` is a pawn move that attacks an enemy pawn, creating tension.
"""

from __future__ import annotations

import chess

from ..features import (
    is_backward_pawn,
    is_doubled_pawn,
    is_isolated_pawn,
    is_passed_pawn,
    pawn_island_count,
)
from .base import DetectionContext, ThemeHit, detector

__all__ = [
    "detect_backward_pawn",
    "detect_creates_isolated_pawn",
    "detect_creates_passed_pawn",
    "detect_doubled_pawn",
    "detect_isolated_pawn",
    "detect_passed_pawn",
    "detect_pawn_break",
    "detect_pawn_island",
]


def _own_pawns(board: chess.Board, side: chess.Color) -> set[chess.Square]:
    return set(chess.SquareSet(board.pawns & board.occupied_co[side]))


def _passed(board: chess.Board, side: chess.Color) -> set[chess.Square]:
    return {sq for sq in _own_pawns(board, side) if is_passed_pawn(board, sq, side)}


def _isolated(board: chess.Board, side: chess.Color) -> set[chess.Square]:
    return {sq for sq in _own_pawns(board, side) if is_isolated_pawn(board, sq, side)}


def _doubled(board: chess.Board, side: chess.Color) -> set[chess.Square]:
    return {sq for sq in _own_pawns(board, side) if is_doubled_pawn(board, sq, side)}


def _backward(board: chess.Board, side: chess.Color) -> set[chess.Square]:
    return {sq for sq in _own_pawns(board, side) if is_backward_pawn(board, sq, side)}


def _first(squares: set[chess.Square]) -> chess.Square:
    return sorted(squares)[0]


@detector
def detect_passed_pawn(ctx: DetectionContext) -> ThemeHit | None:
    """The mover has a passed pawn after the move."""
    squares = _passed(ctx.after, ctx.side)
    if not squares:
        return None
    sq = _first(squares)
    return ThemeHit(
        theme="passed_pawn",
        squares=ctx.squares(sq),
        pieces=ctx.pieces(ctx.after, sq),
        evidence=f"passed pawn on {chess.square_name(sq)}",
    )


@detector
def detect_creates_passed_pawn(ctx: DetectionContext) -> ThemeHit | None:
    """The move produces the mover's first passed pawn."""
    before = _passed(ctx.board, ctx.side)
    after = _passed(ctx.after, ctx.side)
    if not after or before:
        return None
    sq = _first(after)
    return ThemeHit(
        theme="creates_passed_pawn",
        squares=ctx.squares(sq),
        pieces=ctx.pieces(ctx.after, sq),
        evidence=f"the move creates a passed pawn on {chess.square_name(sq)}",
    )


@detector
def detect_isolated_pawn(ctx: DetectionContext) -> ThemeHit | None:
    """The mover has an isolated pawn after the move."""
    squares = _isolated(ctx.after, ctx.side)
    if not squares:
        return None
    sq = _first(squares)
    return ThemeHit(
        theme="isolated_pawn",
        squares=ctx.squares(sq),
        pieces=ctx.pieces(ctx.after, sq),
        evidence=f"isolated pawn on {chess.square_name(sq)}",
    )


@detector
def detect_creates_isolated_pawn(ctx: DetectionContext) -> ThemeHit | None:
    """The move produces the mover's first isolated pawn."""
    before = _isolated(ctx.board, ctx.side)
    after = _isolated(ctx.after, ctx.side)
    if not after or before:
        return None
    sq = _first(after)
    return ThemeHit(
        theme="creates_isolated_pawn",
        squares=ctx.squares(sq),
        pieces=ctx.pieces(ctx.after, sq),
        evidence=f"the move creates an isolated pawn on {chess.square_name(sq)}",
    )


@detector
def detect_doubled_pawn(ctx: DetectionContext) -> ThemeHit | None:
    """The mover has a doubled pawn after the move."""
    squares = _doubled(ctx.after, ctx.side)
    if not squares:
        return None
    sq = _first(squares)
    return ThemeHit(
        theme="doubled_pawn",
        squares=ctx.squares(sq),
        pieces=ctx.pieces(ctx.after, sq),
        evidence=f"doubled pawns on the {chess.FILE_NAMES[chess.square_file(sq)]}-file",
    )


@detector
def detect_backward_pawn(ctx: DetectionContext) -> ThemeHit | None:
    """The mover has a backward pawn after the move."""
    squares = _backward(ctx.after, ctx.side)
    if not squares:
        return None
    sq = _first(squares)
    return ThemeHit(
        theme="backward_pawn",
        confidence=0.7,
        squares=ctx.squares(sq),
        pieces=ctx.pieces(ctx.after, sq),
        evidence=f"backward pawn on {chess.square_name(sq)}",
    )


@detector
def detect_pawn_island(ctx: DetectionContext) -> ThemeHit | None:
    """The number of the mover's pawn islands changed."""
    before = pawn_island_count(ctx.board, ctx.side)
    after = pawn_island_count(ctx.after, ctx.side)
    if before == after:
        return None
    return ThemeHit(
        theme="pawn_island",
        confidence=0.7,
        evidence=f"pawn island count changes from {before} to {after}",
    )


@detector
def detect_pawn_break(ctx: DetectionContext) -> ThemeHit | None:
    """The move is a pawn move that attacks an enemy pawn, creating tension."""
    moved = ctx.moved_piece
    if moved is None or moved.piece_type != chess.PAWN:
        return None
    enemy_pawns = ctx.after.pawns & ctx.after.occupied_co[ctx.opponent]
    if not ctx.after.attacks_mask(ctx.to_square) & enemy_pawns:
        return None
    return ThemeHit(
        theme="pawn_break",
        squares=ctx.squares(ctx.to_square),
        pieces=ctx.pieces(ctx.after, ctx.to_square),
        evidence=f"pawn on {chess.square_name(ctx.to_square)} attacks an enemy pawn",
    )
