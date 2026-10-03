"""Static Exchange Evaluation (SEE): what does this capture sequence really gain?

The usual question "what does this capture really win?" answered by minimax over the
exchange: after the first capture, either side may recapture or walk away, so the value is
the best result for the mover against the opponent's best reply. Both sides' capturers are
collected once (cheapest first) and the "who takes next, and when does the line stop" game is
solved exactly by a small dynamic program -- cheaper than enumerating sequences, and exact
for captures that no linear swap-off gets right (a recapture that the opponent would rather
avoid, or a capture that hangs a piece even though the target is defended).

Why this module exists
----------------------
Several detectors need the *exchange* value of a move rather than its engine evaluation:

* :mod:`moveexp.themes.material` must tell a real sacrifice (the exchange loses material
  but the position improves) from a blunder that merely captures something.
* :mod:`moveexp.themes.tactics` uses "does this move win the exchange" to check that a
  fork or a trap survives the opponent's best reply.
* :mod:`moveexp.themes.tactics` also uses it to reject self-defeating "forks" that merely
  hang the moved piece.

Design rules
------------
* SEE is a **static** approximation: it only reads the current position and never searches.
  It therefore says nothing about pins, discovered checks or tactics deeper than the
  exchange sequence -- the engine still has the final word (see ``classify_special``).
* It is a pure function of the board: no engine calls, no cache, no I/O.
* Piece values come from :data:`moveexp.config.PIECE_VALUE_CP`, so the scale can be
  re-tuned in one place; the algorithm never hard-codes a value.

Sign convention: **positive = the side that captured first ends up ahead** by that many
centi-pawns. For a quiet move the "side that captured first" is the mover, and the answer
is ``0`` because nothing was taken.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from functools import cache

import chess

from ..config import PIECE_VALUE_CP, SACRIFICE_MARGIN_CP, SACRIFICE_MIN_PIECE_CP

__all__ = [
    "SeeResult",
    "is_sacrifice",
    "piece_cp",
    "piece_value_cp",
    "see_after_move",
    "see_capture",
    "static_exchange",
]


def piece_value_cp(piece_type: int, *, values: Mapping[str, int] | None = None) -> int:
    """Centi-pawn value of a python-chess ``piece_type()`` constant.

    :param values: override table keyed by piece *symbol* (``"n"``, ``"q"``, ...).
    :raises ValueError: if the piece type has no value in the table.
    """
    table = PIECE_VALUE_CP if values is None else values
    name = chess.piece_symbol(piece_type)
    if name not in table:
        raise ValueError(f"no configured value for piece type {name!r}")
    return table[name]


def piece_cp(piece: chess.Piece | None, *, values: Mapping[str, int] | None = None) -> int:
    """Centi-pawn value of a piece, ``0`` for an empty square (and 0 for a king)."""
    return 0 if piece is None else piece_value_cp(piece.piece_type, values=values)


def _attacker_values(
    board: chess.Board,
    square: chess.Square,
    side: chess.Color,
    values: Mapping[str, int],
) -> list[int]:
    """Values of every piece of ``side`` that can capture on ``square``, cheapest first.

    Both capture lists of an exchange are read from the *position before the exchange*, which
    is what makes this cheap, but that position is not the right one to generate moves from
    in every case, so two stand-ins are used:

    * **Our own piece on the square** (the recapture case: the side to move there is the one
      that just captured, so its own piece is what an opponent would take). It is swapped for
      an enemy pawn, which occupies the same square -- identical blockers and checks -- while
      making the recaptures legal pawn pushes no more and less than the real captures.
    * **Nothing on the square** (en passant, where the pawn stands next to the target). Same
      substitution, so the capture is generated normally.

    Kings are **excluded**: "king takes rook" is not an exchange ply, it is the end of the
    line. This is the standard SEE simplification and the reason SEE can overestimate a move
    that simply walks into a king recapture -- the engine check in ``classify_special`` is
    what catches that.
    """
    probe = board.copy(stack=False)
    occupant = probe.piece_at(square)
    if occupant is None or occupant.color == side:
        probe.set_piece_at(square, chess.Piece(chess.PAWN, not side))
    # Move generation has to be done *for the side being queried*: `copy()` keeps the side to
    # move, and scanning the opponent's move list instead finds nothing at all.
    probe.turn = side
    found: list[int] = []
    for move in probe.legal_moves:
        if move.to_square != square:
            continue
        piece = probe.piece_at(move.from_square)
        if piece is None or piece.color != side or piece.piece_type == chess.KING:
            continue
        found.append(piece_value_cp(piece.piece_type, values=values))
    found.sort()
    return found


def static_exchange(
    board: chess.Board,
    square: chess.Square,
    side: chess.Color,
    *,
    first_attacker_value: int | None = None,
    victim_value: int | None = None,
    values: Mapping[str, int] | None = None,
) -> int:
    """Swap-off evaluation of the piece on ``square``, for ``side`` to start.

    Both sides' capturers are collected once, cheapest first, and the "who captures next and
    when do we stop" game is solved exactly with a small dynamic program over the two
    indices. That is cheaper than enumerating capture sequences, easier to verify than the
    linear swap-off, and independent of the order in which equally cheap pieces are
    considered.

    :param board: the position *before* the first capture; ``square`` must hold an enemy
        piece of ``side``.
    :param side: the side that plays the first capture.
    :param first_attacker_value: value of the piece that is *actually* going to capture
        (used by :func:`see_capture`, where the move is known). Without it ``side`` plays its
        **best** capture on the square, which is what makes this function answer "what is
        this square worth to ``side``" as well as "what does this capture win". The first
        capture is mandatory either way: SEE answers "what does this capture gain", never
        "should we capture".
    :returns: net centi-pawn gain for ``side``, positive when ``side`` wins material.
        ``0`` when ``square`` is empty or holds a friendly piece.
    """
    table = PIECE_VALUE_CP if values is None else values
    target = board.piece_at(square)
    if victim_value is None:
        if target is None or target.color == side:
            return 0
        victim = piece_value_cp(target.piece_type, values=table)
    else:
        # En passant: the pawn being captured stands on the square *next* to the target.
        victim = victim_value
    own = _attacker_values(board, square, side, table)
    theirs = _attacker_values(board, square, not side, table)
    if first_attacker_value is not None:
        # Put the real attacker first and drop one interchangeable piece of that value.
        own = [first_attacker_value] + [v for v in own if v != first_attacker_value]
    if not own:
        return 0

    # Accounting: capturing the standing piece *gains* its value, and every capture by the
    # opponent costs us exactly the piece standing there (which is the one we just put
    # down). So a capture never "costs" the attacker's value up front -- only being recaptured
    # does. That is what makes an uncontested capture come out as the full victim value.
    @cache
    def best(own_index: int, their_index: int, own_turn: bool) -> int:
        """Best net gain for ``side`` from here on, in centi-pawns.

        ``own_index``/``their_index`` are how many capturers of each side have been used, so
        the piece standing on the square is ``own[own_index - 1]`` or
        ``theirs[their_index - 1]`` -- or the original victim before anybody has captured.
        Both sides may decline to continue (worth ``0`` for us), except at the root, where
        the first capture is mandatory.
        """
        if own_turn:
            standing = theirs[their_index - 1] if their_index else victim
            options: list[int] = [0] if (own_index or their_index) else []
            if own_index < len(own):
                options.append(standing + best(own_index + 1, their_index, False))
            if own_index == 0 and their_index == 0:
                # Root: only the first (given) attacker may capture.
                return options[0]
            # Any of our remaining capturers may take the standing piece.
            for k in range(own_index + 1, len(own)):
                options.append(standing + best(k + 1, their_index, False))
            return max(options)

        standing = own[own_index - 1] if own_index else victim
        options = [0]
        for m in range(their_index, len(theirs)):
            options.append(-standing + best(own_index, m + 1, True))
        return min(options)

    return best(0, 0, True)


@dataclass(frozen=True)
class SeeResult:
    """One SEE query with the numbers detectors and audits want to see."""

    gain_cp: int
    """Net exchange value for the side that played the capture, in centi-pawns."""

    gainer: chess.Color | None
    """Side that ends up ahead by ``gain_cp``; ``None`` for an even exchange."""

    target_value_cp: int
    """Value of the piece on the capture square before the exchange (``0`` if none)."""

    attacker_value_cp: int
    """Value of the piece that played the move (``0`` for a null result)."""

    @property
    def is_win(self) -> bool:
        """The exchange wins material (by more than the sacrifice margin)."""
        return self.gain_cp > SACRIFICE_MARGIN_CP

    @property
    def is_loss(self) -> bool:
        """The exchange loses material (by more than the sacrifice margin)."""
        return self.gain_cp < -SACRIFICE_MARGIN_CP

    @property
    def is_even(self) -> bool:
        """A fair trade, within the margin in both directions."""
        return not self.is_win and not self.is_loss


def _result(gain_cp: int, target_cp: int, attacker_cp: int, side: chess.Color) -> SeeResult:
    if gain_cp > SACRIFICE_MARGIN_CP:
        gainer: chess.Color | None = side
    elif gain_cp < -SACRIFICE_MARGIN_CP:
        gainer = not side
    else:
        gainer = None
    return SeeResult(
        gain_cp=gain_cp,
        gainer=gainer,
        target_value_cp=target_cp,
        attacker_value_cp=attacker_cp,
    )


def see_capture(
    board: chess.Board,
    move: chess.Move,
    *,
    values: Mapping[str, int] | None = None,
) -> SeeResult:
    """SEE of the exchange started by the capture ``move``.

    :param board: the position **before** ``move`` is played.
    :raises ValueError: if ``move`` is not a capture or not legal.
    """
    if not board.is_capture(move):
        raise ValueError(f"{board.uci(move)} is not a capture")
    if move not in board.legal_moves:
        raise ValueError(f"{board.uci(move)} is not legal in {board.fen()}")
    table = PIECE_VALUE_CP if values is None else values
    mover = board.turn
    attacker = piece_cp(board.piece_at(move.from_square), values=table)
    if board.is_en_passant(move):
        target = table["p"]
    else:
        target = piece_cp(board.piece_at(move.to_square), values=table)
    gain = static_exchange(
        board,
        move.to_square,
        mover,
        first_attacker_value=attacker,
        victim_value=target if board.is_en_passant(move) else None,
        values=table,
    )
    return _result(gain, target, attacker, mover)


def see_after_move(
    board: chess.Board,
    move: chess.Move,
    *,
    values: Mapping[str, int] | None = None,
) -> SeeResult:
    """SEE of the exchange that ``move`` leaves on its destination square.

    Works for **every** legal move, so detectors never have to branch on captures:

    * a quiet move captures nothing on the destination square, so the answer is ``0``;
    * a capture evaluates the whole exchange exactly like :func:`see_capture`;
    * a king move (or a move of a piece that can never be exchanged) is likewise ``0``.

    :param board: the position **before** ``move`` is played.
    :raises ValueError: if ``move`` is not legal.
    """
    if move not in board.legal_moves:
        raise ValueError(f"{board.uci(move)} is not legal in {board.fen()}")
    table = PIECE_VALUE_CP if values is None else values
    if not board.is_capture(move):
        attacker = piece_cp(board.piece_at(move.from_square), values=table)
        return SeeResult(gain_cp=0, gainer=None, target_value_cp=0, attacker_value_cp=attacker)
    return see_capture(board, move, values=table)


def is_sacrifice(
    board: chess.Board,
    move: chess.Move,
    *,
    margin_cp: int = SACRIFICE_MARGIN_CP,
    min_piece_cp: int = SACRIFICE_MIN_PIECE_CP,
    values: Mapping[str, int] | None = None,
) -> tuple[bool, int]:
    """Does ``move`` give up material on purpose?

    Operationalised as: the exchange loses more than ``margin_cp`` **and** the piece given
    up is worth at least ``min_piece_cp``. A pawn-for-pawn capture is not a sacrifice in any
    useful sense, so it is excluded by the second condition.

    This function deliberately does **not** look at the engine evaluation: deciding that a
    sacrifice is *correct* needs the position's value, which belongs to the caller
    (``classify_special(sacrifice_confirmed=...)``).

    The returned gain is always the real exchange value, even when the boolean is ``False``
    because the mover was too cheap to be sacrificing anything -- callers get the same answer
    whether or not the second condition applied.

    :returns: ``(is_sacrifice, see_gain_cp)``.
    """
    table = PIECE_VALUE_CP if values is None else values
    see = see_after_move(board, move, values=table)
    piece = board.piece_at(move.from_square)
    if piece is None or piece.piece_type == chess.KING:
        return False, see.gain_cp
    if piece_value_cp(piece.piece_type, values=table) < min_piece_cp:
        return False, see.gain_cp
    return see.gain_cp < -margin_cp, see.gain_cp
