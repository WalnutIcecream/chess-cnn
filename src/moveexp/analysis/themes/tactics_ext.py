"""Puzzle-tag tactics that the core detectors did not cover.

Two groups live here, and the split matters:

* **Static** detectors read the same two positions as the rest of the layer. They mirror the
  Lichess puzzle tags that survive being reduced to a single position (``attackingF2F7``,
  ``capturingDefender``, ``enPassant``, ``advancedPawn``, ...).
* **Line-aware** detectors read :attr:`DetectionContext.continuation` and return ``None``
  when it is absent. ``attraction``, ``clearance`` and ``intermezzo`` are facts about the
  *line* -- a piece is only "attracted" if the opponent actually takes it -- which is why
  ``decoy`` was deliberately absent before the continuation existed (see ``tactics.py``).

Every hit carries evidence, and the definitions are kept conservative on purpose: the puzzle
benchmark (:mod:`eval.puzzle_benchmark`) measures precision against human-curated tags, and a
detector that fires on every move is worse than one that fires rarely and is right.
"""

from __future__ import annotations

import chess

from ...config import (
    HANGING_MIN_PIECE_CP,
    HANGING_PIECE_MIN_NET_ATTACKERS,
    SACRIFICE_MARGIN_CP,
)
from ..features import is_passed_pawn
from ..see import see_after_move
from .base import DetectionContext, ThemeHit, detector
from .common import net_attackers, piece_value

__all__ = [
    "detect_advanced_pawn",
    "detect_attacking_f2f7",
    "detect_attraction",
    "detect_capturing_defender",
    "detect_clearance",
    "detect_defensive_move",
    "detect_en_passant",
    "detect_intermezzo",
    "detect_kingside_attack",
    "detect_queenside_attack",
    "detect_quiet_move",
    "detect_smothered_mate",
    "detect_under_promotion",
    "detect_zugzwang",
]

#: Files that make up the two wings of the board, used by the wing-pressure detectors.
_KINGSIDE_FILES = (5, 6, 7)
_QUEENSIDE_FILES = (0, 1, 2)

#: A zugzwang claim is a strong one, so it is only made when the opponent is nearly
#: immobile; a wide-open position is not a bind however bad its moves are.
_ZUGZWANG_MAX_REPLIES = 6


def _enemy_squares(board: chess.Board, side: chess.Color) -> list[chess.Square]:
    """Squares holding a non-king enemy piece (kings are handled where relevant)."""
    mask = board.occupied_co[not side] & ~board.kings
    return list(chess.SquareSet(mask))


def _wing_attack(ctx: DetectionContext, files: tuple[int, ...], label: str) -> ThemeHit | None:
    """Shared body of the kingside/queenside attack detectors.

    Firing on "the mover attacks squares on that wing" would match almost every move (a rook
    lift attacks a whole rank), so the bar is an attack on an enemy *piece* on the wing --
    the king included, which is just a check. Measured against the puzzle tags this is the
    difference between precision 0.15 and a usable detector.
    """
    enemy_king = ctx.after.king(ctx.opponent)
    if enemy_king is None or chess.square_file(enemy_king) not in files:
        return None
    moved = chess.BB_SQUARES[ctx.to_square]
    ranks = range(4, 8) if ctx.opponent == chess.BLACK else range(0, 4)
    for rank in ranks:
        for file in files:
            square = chess.square(file, rank)
            piece = ctx.after.piece_at(square)
            if piece is None or piece.color != ctx.opponent:
                continue
            if ctx.after.attackers_mask(ctx.side, square) & moved:
                return ThemeHit(
                    theme="kingside_attack" if files == _KINGSIDE_FILES else "queenside_attack",
                    confidence=0.6,
                    squares=ctx.squares(ctx.to_square, square),
                    pieces=ctx.pieces(ctx.after, ctx.to_square),
                    evidence=(
                        f"the move attacks {ctx.pieces(ctx.after, square)[0]} on the enemy "
                        f"king's {label}"
                    ),
                )
    return None


@detector
def detect_kingside_attack(ctx: DetectionContext) -> ThemeHit | None:
    """The enemy king is on the kingside and this move adds pressure there."""
    return _wing_attack(ctx, _KINGSIDE_FILES, "kingside")


@detector
def detect_queenside_attack(ctx: DetectionContext) -> ThemeHit | None:
    """The enemy king is on the queenside and this move adds pressure there."""
    return _wing_attack(ctx, _QUEENSIDE_FILES, "queenside")


@detector
def detect_en_passant(ctx: DetectionContext) -> ThemeHit | None:
    """The move captures en passant -- a capture whose victim is not on the target square."""
    if not ctx.is_ep:
        return None
    victim = chess.square(chess.square_file(ctx.to_square), chess.square_rank(ctx.from_square))
    return ThemeHit(
        theme="en_passant",
        squares=ctx.squares(ctx.from_square, ctx.to_square, victim),
        pieces=ctx.pieces(ctx.after, ctx.to_square),
        evidence=(
            f"{ctx.san()} takes on {chess.square_name(ctx.to_square)} en passant, removing the "
            f"pawn on {chess.square_name(victim)}"
        ),
    )


@detector
def detect_under_promotion(ctx: DetectionContext) -> ThemeHit | None:
    """The move promotes to something other than a queen."""
    if not ctx.is_promotion or ctx.move.promotion == chess.QUEEN:
        return None
    name = chess.piece_name(ctx.move.promotion) if ctx.move.promotion else "piece"
    return ThemeHit(
        theme="under_promotion",
        squares=ctx.squares(ctx.from_square, ctx.to_square),
        pieces=ctx.pieces(ctx.after, ctx.to_square),
        evidence=f"{ctx.san()} promotes to a {name}, not a queen",
    )


@detector
def detect_capturing_defender(ctx: DetectionContext) -> ThemeHit | None:
    """The capture removes the *sole* defender of another enemy piece we are attacking."""
    if not ctx.is_capture:
        return None
    captured = ctx.to_square
    for target in _enemy_squares(ctx.after, ctx.side):
        if target == captured:
            continue
        # Before the move the captured piece had to be the only defender of the target...
        if ctx.board.attackers_mask(ctx.opponent, target) != chess.BB_SQUARES[captured]:
            continue
        # ...and we have to be attacking the target now that the guard is gone.
        if not ctx.after.attackers_mask(ctx.side, target) & ctx.after.occupied_co[ctx.side]:
            continue
        return ThemeHit(
            theme="capturing_defender",
            confidence=0.7,
            squares=ctx.squares(captured, target),
            pieces=ctx.pieces(ctx.after, target),
            evidence=(
                f"{ctx.san()} removes the only defender of {ctx.pieces(ctx.after, target)[0]}"
            ),
        )
    return None


@detector
def detect_attacking_f2f7(ctx: DetectionContext) -> ThemeHit | None:
    """The move attacks the f2/f7 square in front of the enemy king, where there is a piece."""
    rank = 6 if ctx.opponent == chess.BLACK else 1
    target = chess.square(chess.FILE_NAMES.index("f"), rank)
    if ctx.after.piece_at(target) is None:
        return None
    if not ctx.after.attackers_mask(ctx.side, target) & chess.BB_SQUARES[ctx.to_square]:
        return None
    before = (
        ctx.board.attackers_mask(ctx.side, target) & ctx.board.occupied_co[ctx.side]
    ).bit_count()
    after = (
        ctx.after.attackers_mask(ctx.side, target) & ctx.after.occupied_co[ctx.side]
    ).bit_count()
    if after <= before:
        return None
    return ThemeHit(
        theme="attacking_f2f7",
        confidence=0.7,
        squares=ctx.squares(ctx.to_square, target),
        pieces=ctx.pieces(ctx.after, target),
        evidence=(
            f"the move attacks {ctx.pieces(ctx.after, target)[0]} on "
            f"{chess.square_name(target)}, in front of the enemy king"
        ),
    )


@detector
def detect_smothered_mate(ctx: DetectionContext) -> ThemeHit | None:
    """Mate delivered to a king whose every escape square is blocked by its own pieces."""
    if not ctx.is_mate:
        return None
    king = ctx.after.king(ctx.opponent)
    if king is None:
        return None
    ring = list(chess.SquareSet(chess.BB_KING_ATTACKS[king]))
    if not ring:
        return None
    if not all(
        (piece := ctx.after.piece_at(square)) is not None and piece.color == ctx.opponent
        for square in ring
    ):
        return None
    return ThemeHit(
        theme="smothered_mate",
        squares=ctx.squares(ctx.to_square, king),
        pieces=ctx.pieces(ctx.after, ctx.to_square),
        evidence=(
            f"{ctx.san()} mates: the king on {chess.square_name(king)} is entirely surrounded "
            f"by its own pieces"
        ),
    )


def _reply_loses_material(board: chess.Board, reply: chess.Move) -> bool:
    """Does allowing ``reply`` let the opponent win material on their next move?

    A cheap static proxy for "this reply is bad": push the reply and look for any capture the
    other side then wins by SEE. No search, so it understates quiet positional binds -- which
    is deliberate, because those would make the detector fire everywhere.
    """
    after = board.copy(stack=False)
    after.push(reply)
    return any(
        after.is_capture(candidate)
        and see_after_move(after, candidate).gain_cp > SACRIFICE_MARGIN_CP
        for candidate in after.legal_moves
    )


@detector
def detect_zugzwang(ctx: DetectionContext) -> ThemeHit | None:
    """The opponent is not in check, is nearly immobile, and every reply loses material."""
    board = ctx.after
    if board.is_check() or board.is_game_over():
        return None
    replies = list(board.legal_moves)
    if not replies or len(replies) > _ZUGZWANG_MAX_REPLIES:
        return None
    if not all(_reply_loses_material(board, reply) for reply in replies):
        return None
    return ThemeHit(
        theme="zugzwang",
        confidence=0.5,
        squares=ctx.squares(ctx.to_square),
        pieces=ctx.pieces(ctx.after, ctx.to_square),
        evidence=(
            f"after {ctx.san()} the opponent has only {len(replies)} replies and every one "
            f"of them loses material"
        ),
    )


@detector
def detect_defensive_move(ctx: DetectionContext) -> ThemeHit | None:
    """The move makes safe a piece of ours that was genuinely hanging before it."""
    for square, piece in ctx.board.piece_map().items():
        if piece.color != ctx.side or piece.piece_type == chess.KING:
            continue
        if piece_value(piece) < HANGING_MIN_PIECE_CP:
            continue
        if net_attackers(ctx.board, square, ctx.opponent) < HANGING_PIECE_MIN_NET_ATTACKERS:
            continue
        was_hanging = (
            net_attackers(ctx.after, square, ctx.opponent) >= HANGING_PIECE_MIN_NET_ATTACKERS
        )
        if was_hanging:
            continue
        label = (
            ctx.pieces(ctx.after, square)[0]
            if ctx.after.piece_at(square) is not None
            else ctx.pieces(ctx.board, square)[0]
        )
        return ThemeHit(
            theme="defensive_move",
            confidence=0.7,
            squares=ctx.squares(square, ctx.to_square),
            pieces=ctx.pieces(ctx.after, square) + ctx.pieces(ctx.after, ctx.to_square),
            evidence=f"the hanging {label} is made safe by {ctx.san()}",
        )
    return None


@detector
def detect_advanced_pawn(ctx: DetectionContext) -> ThemeHit | None:
    """The move pushes a pawn deep into the enemy half where it becomes a passed pawn."""
    piece = ctx.moved_piece
    if piece is None or piece.piece_type != chess.PAWN or ctx.is_promotion:
        return None
    square = ctx.to_square
    rank = chess.square_rank(square)
    advanced = rank >= 5 if ctx.side == chess.WHITE else rank <= 2
    if not advanced:
        return None
    landed = ctx.after.piece_at(square)
    if landed is None or landed.piece_type != chess.PAWN:
        return None
    if not is_passed_pawn(ctx.after, square, ctx.side):
        return None
    steps = 7 - rank if ctx.side == chess.WHITE else rank
    return ThemeHit(
        theme="advanced_pawn",
        squares=ctx.squares(ctx.from_square, square),
        pieces=ctx.pieces(ctx.after, square),
        evidence=(
            f"the pawn reaches {chess.square_name(square)}, a passed pawn {steps} step(s) from "
            f"promotion"
        ),
    )


@detector
def detect_quiet_move(ctx: DetectionContext) -> ThemeHit | None:
    """A quiet move (no capture, check or promotion) that leaves a real threat behind it.

    Ungated, "the move is quiet" is true of most moves, so the definition additionally
    requires the quiet move to attack a valuable enemy piece that is insufficiently
    defended. That is the shape of the quiet wins the Lichess tag names.
    """
    if ctx.is_capture or ctx.is_check or ctx.is_promotion or ctx.is_castling:
        return None
    moved = chess.BB_SQUARES[ctx.to_square]
    for square in _enemy_squares(ctx.after, ctx.side):
        if piece_value(ctx.after.piece_at(square)) < HANGING_MIN_PIECE_CP:
            continue
        if not ctx.after.attackers_mask(ctx.side, square) & moved:
            continue
        if net_attackers(ctx.after, square, ctx.side) < HANGING_PIECE_MIN_NET_ATTACKERS:
            continue
        already = bool(ctx.board.attackers_mask(ctx.side, square) & ctx.board.occupied_co[ctx.side])
        if already:
            continue
        return ThemeHit(
            theme="quiet_move",
            confidence=0.6,
            squares=ctx.squares(ctx.to_square, square),
            pieces=ctx.pieces(ctx.after, ctx.to_square),
            evidence=(
                f"the quiet {ctx.san()} leaves {ctx.pieces(ctx.after, square)[0]} under threat"
            ),
        )
    return None


@detector
def detect_attraction(ctx: DetectionContext) -> ThemeHit | None:
    """A sacrifice lures an enemy piece onto a square where the following move wins it.

    Line-aware: needs the opponent's reply *and* the mover's next move. Fires only when the
    opponent actually captures on the offered square (takes the bait) and the next move
    punishes it with a capture or a check.
    """
    if len(ctx.continuation) < 2:
        return None
    reply, follow = ctx.continuation[0], ctx.continuation[1]
    if not ctx.after.is_capture(reply) or reply.to_square != ctx.to_square:
        return None
    boards = ctx.continuation_boards
    if not boards:
        return None  # the recorded reply is not legal here: nothing to reason about
    board_after_reply = boards[0]
    if follow not in board_after_reply.legal_moves:
        return None
    if not (board_after_reply.is_capture(follow) or board_after_reply.gives_check(follow)):
        return None
    return ThemeHit(
        theme="attraction",
        confidence=0.6,
        squares=ctx.squares(ctx.to_square, follow.to_square),
        pieces=ctx.pieces(board_after_reply, follow.to_square),
        evidence=(
            f"the offer on {chess.square_name(ctx.to_square)} draws the reply "
            f"{ctx.after.san(reply)}, and the follow-up wins on "
            f"{chess.square_name(follow.to_square)}"
        ),
    )


@detector
def detect_clearance(ctx: DetectionContext) -> ThemeHit | None:
    """The move vacates a square (or a line) that the mover's *next* move needs.

    Line-aware: fires when the follow-up is a capture or a check that passes through, lands
    on, or exploits the square the move just left. The clearing move itself must be quiet --
    a capture is doing something with its own square, not preparing another piece's.
    """
    if ctx.is_capture:
        return None
    if len(ctx.continuation) < 2:
        return None
    follow = ctx.continuation[1]
    boards = ctx.continuation_boards
    if not boards:
        return None
    board_after_reply = boards[0]
    if follow not in board_after_reply.legal_moves:
        return None
    if not (board_after_reply.is_capture(follow) or board_after_reply.gives_check(follow)):
        return None
    vacated = ctx.from_square
    used = follow.from_square == vacated or follow.to_square == vacated
    if not used:
        used = bool(chess.BB_SQUARES[vacated] & chess.between(follow.from_square, follow.to_square))
    if not used:
        return None
    return ThemeHit(
        theme="clearance",
        confidence=0.5,
        squares=ctx.squares(vacated, follow.from_square, follow.to_square),
        pieces=ctx.pieces(board_after_reply, follow.from_square),
        evidence=(
            f"vacating {chess.square_name(vacated)} lets the follow-up "
            f"{board_after_reply.san(follow)} through"
        ),
    )


@detector
def detect_intermezzo(ctx: DetectionContext) -> ThemeHit | None:
    """A forcing in-between move, played before the expected recapture.

    Line-aware: fires when the move is itself forcing (a capture or a check, so an exchange or
    a mate threat is genuinely in progress), the opponent replies *without* recapturing on the
    mover's square, and the mover's next move is also a check or a capture -- an insertion,
    not a continuation of the sequence.
    """
    if not (ctx.is_capture or ctx.is_check):
        return None  # no tension exists for an in-between move to interrupt
    if len(ctx.continuation) < 2:
        return None
    reply, in_between = ctx.continuation[0], ctx.continuation[1]
    boards = ctx.continuation_boards
    if not boards:
        return None
    board_after_reply = boards[0]
    if ctx.after.is_capture(reply) and reply.to_square == ctx.to_square:
        return None  # the expected recapture: this is a trade, not an intermezzo
    if in_between not in board_after_reply.legal_moves:
        return None
    if not (board_after_reply.gives_check(in_between) or board_after_reply.is_capture(in_between)):
        return None
    return ThemeHit(
        theme="intermezzo",
        confidence=0.5,
        squares=ctx.squares(ctx.to_square, in_between.from_square, in_between.to_square),
        pieces=ctx.pieces(board_after_reply, in_between.from_square),
        evidence=(
            f"{board_after_reply.san(in_between)} is played in between, before the recapture is "
            f"completed"
        ),
    )
