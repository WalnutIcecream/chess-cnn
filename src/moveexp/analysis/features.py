"""Positional features: what did this move change, besides the evaluation?

The engine says *whether* a move is better. This module says *what* it changed, in six
coarse groups that :class:`moveexp.schema.PositionalDelta` carries to the language layer:

======================  =====================================================
``material``            net centi-pawn swing (after - before)
``mobility``            squares attacked by the side's pieces, pawns excluded
``king_safety``         own pawn shield minus enemy pressure around the own king
``pawn_structure``      quality score: doubled/isolated/backward penalties, passed bonus
``space``               centre squares the side attacks
``activity``            centralisation of the pieces, plus outposts and open files
======================  =====================================================

Design rules
------------
* **Pure and cheap.** No engine call, no cache, no I/O, no search -- just attack masks and
  pawn counting. It runs for every labelled position, so it has to stay cheap.
* **From the mover's point of view.** ``after - before`` for the side that played the move,
  so a positive number always means "this move improved that aspect", for either colour.
* **Symmetric in colour.** Every number is counted the same way for both sides, so a delta
  never mixes "White thinks" with "Black thinks"; only the sign flips with the perspective of
  the side asked about.
* **Coarse on purpose.** The weights in :data:`moveexp.config.FEATURE_WEIGHTS` put these
  numbers on a roughly pawn-move scale. They are a trend signal for the language layer and
  are never fed back into an evaluation, so there is no point in pretending to be more
  precise than the counts really are.

All the numbers that make these features tunable -- values, weights, bonuses, penalties --
live in :mod:`moveexp.config`; this module only knows how to count.
"""

from __future__ import annotations

from dataclasses import dataclass

import chess

from ..config import (
    ACTIVITY_KING_ZONE_DISTANCE,
    BACKWARD_PAWN_CP,
    CENTRE_SQUARES,
    DOUBLED_PAWN_CP,
    FEATURE_WEIGHTS,
    ISOLATED_PAWN_CP,
    KING_ATTACK_WEIGHT,
    KING_ZONE_RANK_SPAN,
    MINOR_KING_ZONE_BONUS,
    OUTPOST_BONUS,
    OUTPOST_MIN_RELATIVE_RANK,
    OUTPOST_REQUIRES_PAWN_DEFENCE,
    PASSED_PAWN_BONUS_CP,
    PIECE_CENTRALITY,
    PIECE_VALUE_CP,
    ROOK_OPEN_FILE_BONUS,
)
from ..schema import PositionalDelta

__all__ = [
    "FEATURE_GROUPS",
    "FeatureSnapshot",
    "centre_distance",
    "is_backward_pawn",
    "is_doubled_pawn",
    "is_isolated_pawn",
    "is_outpost",
    "is_passed_pawn",
    "king_zone",
    "pawn_file_groups",
    "pawn_island_count",
    "positional_delta",
    "snapshot",
]

#: Feature group names in a fixed order, so reports and tests never depend on dict order.
FEATURE_GROUPS: tuple[str, ...] = tuple(FEATURE_WEIGHTS)

_CENTRE: tuple[chess.Square, ...] = tuple(chess.parse_square(name) for name in CENTRE_SQUARES)


def centre_distance(square: chess.Square) -> int:
    """Distance from ``square`` to the nearest centre square (``0`` = on the centre).

    Uses python-chess's Chebyshev distance, so a knight on c3 counts as one step from d4
    while a rook on a1 counts as three.
    """
    return min(chess.square_distance(square, centre) for centre in _CENTRE)


def king_zone(board: chess.Board, side: chess.Color) -> chess.SquareSet:
    """Squares around ``side``'s king that its safety is measured on.

    ``KING_ZONE_RANK_SPAN`` ranks deep towards the centre and the three files around the
    king, all clamped to the board -- which is what gives a king on the first rank the
    three-rank shield in front of it instead of half a zone behind it.
    """
    king = board.king(side)
    if king is None:
        return chess.SquareSet()
    file_index = chess.square_file(king)
    rank_index = chess.square_rank(king)
    squares = [
        chess.square(f, r)
        for f in range(max(0, file_index - 1), min(7, file_index + 1) + 1)
        for r in range(
            max(0, rank_index - KING_ZONE_RANK_SPAN), min(7, rank_index + KING_ZONE_RANK_SPAN) + 1
        )
    ]
    return chess.SquareSet(squares)


def is_outpost(board: chess.Board, square: chess.Square) -> bool:
    """Is a minor piece on ``square`` an outpost?

    Three conditions, all of them needed: the piece is advanced enough to be in the fight
    (:data:`moveexp.config.OUTPOST_MIN_RELATIVE_RANK`), no enemy pawn can attack the square,
    and a friendly pawn defends it. An outpost is safe *because* the enemy cannot take it
    with a pawn while standing deep in their territory -- a knight on f3 guarded by g2 is
    defended, but it is not an outpost.
    """
    piece = board.piece_at(square)
    if piece is None or piece.piece_type not in (chess.KNIGHT, chess.BISHOP):
        return False
    rank_index = chess.square_rank(square)
    relative_rank = rank_index if piece.color == chess.WHITE else 7 - rank_index
    if relative_rank < OUTPOST_MIN_RELATIVE_RANK:
        return False
    # `attackers_mask` asks "who beats this square"; `attacks_mask` would ask what the piece
    # itself hits, which would make every back-rank minor piece an "outpost".
    if board.attackers_mask(not piece.color, square) & board.pawns:
        return False
    if not OUTPOST_REQUIRES_PAWN_DEFENCE:
        return True
    return bool(board.attackers_mask(piece.color, square) & board.pawns)


def pawn_file_groups(board: chess.Board, side: chess.Color) -> dict[int, list[chess.Square]]:
    """Own pawns grouped by file, ordered by rank (nearest own side first)."""
    by_file: dict[int, list[chess.Square]] = {}
    for square in chess.SquareSet(board.pawns & board.occupied_co[side]):
        by_file.setdefault(chess.square_file(square), []).append(square)
    for squares in by_file.values():
        squares.sort(key=chess.square_rank)
    return by_file


def is_passed_pawn(board: chess.Board, square: chess.Square, side: chess.Color) -> bool:
    """No enemy pawn on this file or a neighbouring file ahead of ``square``."""
    rank_index = chess.square_rank(square)
    step = 1 if side == chess.WHITE else -1
    enemy_pawns = chess.SquareSet(board.pawns & board.occupied_co[not side])
    for enemy_square in enemy_pawns:
        if abs(chess.square_file(enemy_square) - chess.square_file(square)) > 1:
            continue
        if (chess.square_rank(enemy_square) - rank_index) * step > 0:
            return False
    return True


def is_isolated_pawn(board: chess.Board, square: chess.Square, side: chess.Color) -> bool:
    """No friendly pawn on either neighbouring file."""
    file_index = chess.square_file(square)
    by_file = pawn_file_groups(board, side)
    return not by_file.get(file_index - 1) and not by_file.get(file_index + 1)


def is_doubled_pawn(board: chess.Board, square: chess.Square, side: chess.Color) -> bool:
    """More than one friendly pawn on this file."""
    return len(pawn_file_groups(board, side).get(chess.square_file(square), ())) > 1


def is_backward_pawn(board: chess.Board, square: chess.Square, side: chess.Color) -> bool:
    """A pawn that cannot advance without being captured and no friendly pawn can support.

    ``not isolated`` is required because an isolated pawn is its own, worse, flaw; the
    "no friendly pawn can support it" half of the classic definition is what keeps every
    undeveloped opening pawn from counting as backward.
    """
    step = 1 if side == chess.WHITE else -1
    file_index = chess.square_file(square)
    rank_index = chess.square_rank(square)
    neighbours = {
        other
        for other_file in (file_index - 1, file_index + 1)
        for other in pawn_file_groups(board, side).get(other_file, ())
    }
    if not neighbours:
        return False
    supported = any((chess.square_rank(other) - rank_index) * step >= 0 for other in neighbours)
    if supported:
        return False
    return not is_passed_pawn(board, square, side) and _is_stuck(board, square, step)


def pawn_island_count(board: chess.Board, side: chess.Color) -> int:
    """Number of connected pawn groups: a pawn island is a set of files with pawns, each
    file adjacent to the next."""
    files = sorted(pawn_file_groups(board, side))
    if not files:
        return 0
    islands = 1
    for left, right in zip(files, files[1:], strict=False):
        if right - left > 1:
            islands += 1
    return islands


def _material_cp(board: chess.Board, side: chess.Color) -> float:
    """Material balance for ``side``, in centi-pawns."""
    total = 0.0
    for piece in board.piece_map().values():
        value = PIECE_VALUE_CP[piece.symbol().lower()]
        total += value if piece.color == side else -value
    return total


def _mobility(board: chess.Board, side: chess.Color) -> float:
    """Squares attacked by the side's pieces, pawns and king excluded.

    Pawns are excluded because a pawn's reach is a structural fact, already counted by
    ``pawn_structure`` and ``space``; the king is excluded because it belongs to
    ``king_safety``.
    """
    total = 0.0
    free = ~board.occupied_co[side]
    for square, piece in board.piece_map().items():
        if piece.color != side or piece.piece_type in (chess.PAWN, chess.KING):
            continue
        # Friendly-occupied squares are where the piece "defends its own", not where it can go.
        total += len(chess.SquareSet(board.attacks_mask(square) & free))
    return total


def _king_safety(board: chess.Board, side: chess.Color) -> float:
    """Own pawn shield around the king minus enemy pressure on the same zone.

    A zone square attacked by an enemy piece counts ``-1``, and one that only the enemy king
    attacks counts ``-KING_ATTACK_WEIGHT``: a king reaches one step further than a rook but
    only just, so it must not dominate the count.
    """
    zone = king_zone(board, side)
    if not zone:
        return 0.0
    enemy = not side
    enemy_kings = board.kings & board.occupied_co[enemy]
    pressure = 0.0
    shield = 0.0
    for square in zone:
        piece = board.piece_at(square)
        if piece is not None and piece.color == side and piece.piece_type == chess.PAWN:
            shield += 1.0
        attackers = board.attackers_mask(enemy, square) & board.occupied_co[enemy]
        if attackers & ~enemy_kings:
            pressure += 1.0
        elif attackers & enemy_kings:
            pressure += KING_ATTACK_WEIGHT
    return shield - pressure


def _pawn_structure(board: chess.Board, side: chess.Color) -> float:
    """Structure quality: flaws subtract, passed pawns add.

    Doubled, isolated and backward are the classic three flaws, defined in their simplest
    terms so that the count needs no engine:

    * **doubled** -- more than one pawn on a file;
    * **isolated** -- no friendly pawn on a neighbouring file;
    * **backward** -- no friendly pawn can support it *and* it cannot advance without being
      captured. Without the second half of that condition every pawn in the opening would
      count as backward, the term would never change, and the feature would be dead weight.
    """
    by_file = pawn_file_groups(board, side)
    score = 0.0
    for squares in by_file.values():
        score -= DOUBLED_PAWN_CP * (len(squares) - 1)
    for square in chess.SquareSet(board.pawns & board.occupied_co[side]):
        if is_isolated_pawn(board, square, side):
            score -= ISOLATED_PAWN_CP
        elif is_backward_pawn(board, square, side):
            score -= BACKWARD_PAWN_CP
        if is_passed_pawn(board, square, side):
            score += PASSED_PAWN_BONUS_CP
    return score


def _is_stuck(board: chess.Board, square: chess.Square, step: int) -> bool:
    """Can this pawn not step forward without being captured?

    Only an *attacked* advance square counts: a pawn that is simply blocked by a piece is
    blocked, not backward. A pawn that can still advance is merely undeveloped.
    """
    ahead_rank = chess.square_rank(square) + step
    if not 0 <= ahead_rank <= 7:
        return True
    next_square = chess.square(chess.square_file(square), ahead_rank)
    if board.piece_at(next_square) is not None:
        return False
    side = board.color_at(square)
    return bool(board.attackers_mask(not side, next_square) & board.pawns)


def _space(board: chess.Board, side: chess.Color) -> float:
    """Centre squares the side attacks. Own occupation is not space."""
    controlled = chess.SquareSet()
    for square, piece in board.piece_map().items():
        if piece.color == side:
            controlled |= board.attacks_mask(square)
    return float(len(chess.SquareSet(controlled) & chess.SquareSet(_CENTRE)))


def _near_enemy_king(board: chess.Board, square: chess.Square, side: chess.Color) -> bool:
    """Chebyshev distance to the enemy king within ``ACTIVITY_KING_ZONE_DISTANCE``."""
    enemy_king = board.king(not side)
    return (
        enemy_king is not None
        and chess.square_distance(square, enemy_king) <= ACTIVITY_KING_ZONE_DISTANCE
    )


def _has_open_file(board: chess.Board, square: chess.Square) -> bool:
    """True when the square's file holds no pawns at all (semi-open files count too)."""
    return not board.pawns & chess.BB_FILES[chess.square_file(square)]


def _activity(board: chess.Board, side: chess.Color) -> float:
    """Centralisation of the side's pieces, plus outposts and minor pieces in the zone.

    The centrality tables are indexed by :func:`centre_distance`, so the middle of the board
    is worth a lot to a knight or bishop and very little to a rook -- a rook belongs behind
    pawns, not on d4.
    """
    score = 0.0
    for square, piece in board.piece_map().items():
        if piece.color != side:
            continue
        table = PIECE_CENTRALITY.get(piece.symbol().lower())
        if table is not None:
            score += table[min(centre_distance(square), len(table) - 1)]
        if piece.piece_type in (chess.KNIGHT, chess.BISHOP):
            if is_outpost(board, square):
                score += OUTPOST_BONUS
            if _near_enemy_king(board, square, side):
                score += MINOR_KING_ZONE_BONUS
        elif piece.piece_type == chess.ROOK and _has_open_file(board, square):
            score += ROOK_OPEN_FILE_BONUS
    return score


@dataclass(frozen=True)
class FeatureSnapshot:
    """The six feature groups for one side of one position, before weighting."""

    side: chess.Color
    material_cp: float
    mobility: float
    king_safety: float
    pawn_structure: float
    space: float
    activity: float

    def as_tuple(self) -> tuple[float, ...]:
        """Raw group values in :data:`FEATURE_GROUPS` order."""
        return tuple(
            getattr(self, group if group != "material" else "material_cp")
            for group in FEATURE_GROUPS
        )

    def weighted(self) -> tuple[float, ...]:
        """Group values multiplied by :data:`moveexp.config.FEATURE_WEIGHTS`, in group order."""
        return tuple(
            value * FEATURE_WEIGHTS[group]
            for group, value in zip(FEATURE_GROUPS, self.as_tuple(), strict=True)
        )

    def delta_vector(self, before: FeatureSnapshot) -> tuple[float, ...]:
        """Weighted ``self - before`` for the same side, in :data:`FEATURE_GROUPS` order."""
        return tuple(
            after - start for after, start in zip(self.weighted(), before.weighted(), strict=True)
        )

    def delta_from(self, before: FeatureSnapshot) -> PositionalDelta:
        """Weighted ``self - before`` as a :class:`moveexp.schema.PositionalDelta`."""
        return PositionalDelta(**dict(zip(FEATURE_GROUPS, self.delta_vector(before), strict=True)))


def snapshot(board: chess.Board, side: chess.Color) -> FeatureSnapshot:
    """All six groups for ``side`` in ``board``, unweighted."""
    return FeatureSnapshot(
        side=side,
        material_cp=_material_cp(board, side),
        mobility=_mobility(board, side),
        king_safety=_king_safety(board, side),
        pawn_structure=_pawn_structure(board, side),
        space=_space(board, side),
        activity=_activity(board, side),
    )


def positional_delta(board: chess.Board, move: chess.Move) -> PositionalDelta:
    """Weighted change in the six groups caused by ``move``, for the side that played it.

    :param board: the position **before** ``move``.
    :param move: a legal move for the side to move.
    :returns: ``PositionalDelta`` whose fields are ``after - before`` for the mover, so a
        positive field always means the move improved that aspect.
    :raises ValueError: if ``move`` is not legal in ``board``.
    """
    if move not in board.legal_moves:
        raise ValueError(f"{board.uci(move)} is not legal in {board.fen()}")
    side = board.turn
    before = snapshot(board, side)
    after = board.copy(stack=False)
    after.push(move)
    return snapshot(after, side).delta_from(before)
