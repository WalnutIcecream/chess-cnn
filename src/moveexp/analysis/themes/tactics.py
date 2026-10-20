"""Tactical detectors (the ``tactics`` themes).

Every rule here is decided from the two positions only -- no engine, no search -- so a hit is
something a human can verify by looking at the board. One theme is deliberately *absent*:
``decoy`` only exists once the opponent actually takes the bait, which is a reply, not a fact
about the position, so it is left to the engine-backed intent layer rather than guessed at
here.

Conventions:

* "Attacked" always means *by the side that just moved*, on the position *after* the move.
* An attacked king counts as a target worth :data:`~moveexp.analysis.themes.common.king_value_cp`,
  because a fork that also hits the king is the most valuable fork there is.
* Rays are walked by the shared helpers so that "the piece behind the piece" means the same
  thing to the skewer and x-ray rules.
* Each detector reports at most one hit -- the most valuable instance it can see -- so a
  single position cannot flood the report with near-identical lines.
"""

from __future__ import annotations

import chess

from ...config import (
    FORK_MAX_SELF_LOSS_CP,
    FORK_MIN_TARGET_CP,
    HANGING_MIN_PIECE_CP,
    HANGING_PIECE_MIN_NET_ATTACKERS,
)
from .base import DetectionContext, ThemeHit, detector
from .common import (
    king_value_cp,
    net_attackers,
    occupied_attackers,
    piece_value,
)

__all__ = [
    "detect_back_rank_mate",
    "detect_deflection",
    "detect_discovered_attack",
    "detect_discovered_check",
    "detect_double_check",
    "detect_fork",
    "detect_hanging_piece",
    "detect_hanging_piece_defended",
    "detect_interference",
    "detect_overloaded_defender",
    "detect_pin",
    "detect_skewer",
    "detect_threat_created",
    "detect_trapped_piece",
    "detect_x_ray",
]

_ORTHO = ((1, 0), (-1, 0), (0, 1), (0, -1))
_DIAG = ((1, 1), (1, -1), (-1, 1), (-1, -1))

#: What a fork/SEE-less exchange is worth losing the attacking piece for. Same floor as the
#: piece-values table: below a minor, "the knight is not really defended" is not a fork.


def _ray_directions(piece_type: chess.PieceType) -> tuple[tuple[int, int], ...]:
    """Step vectors for a sliding piece; empty for pawns, knights and kings."""
    if piece_type == chess.QUEEN:
        return _ORTHO + _DIAG
    if piece_type == chess.ROOK:
        return _ORTHO
    if piece_type == chess.BISHOP:
        return _DIAG
    return ()


def _ray_occupants(board: chess.Board, square: chess.Square, piece_type: chess.PieceType):
    """Yield one list of occupied squares per ray, nearest first."""
    file0, rank0 = chess.square_file(square), chess.square_rank(square)
    for df, dr in _ray_directions(piece_type):
        f, r = file0 + df, rank0 + dr
        found: list[chess.Square] = []
        while 0 <= f < 8 and 0 <= r < 8:
            s = chess.square(f, r)
            if board.piece_at(s):
                found.append(s)
            f += df
            r += dr
        if found:
            yield found


def _two_piece_rays(board: chess.Board, square: chess.Square, piece_type: chess.PieceType):
    """Yield ``(front, back)`` for each ray holding two or more pieces."""
    for ray in _ray_occupants(board, square, piece_type):
        if len(ray) >= 2:
            yield ray[0], ray[1]


def _pieces_of(
    board: chess.Board, colour: chess.Color, *, kings: bool = False
) -> list[chess.Square]:
    """Squares holding a piece of ``colour``, in square order."""
    mask = board.occupied_co[colour]
    if not kings:
        mask &= ~board.kings
    return list(chess.SquareSet(mask))


def _enemy_pieces(board: chess.Board, colour: chess.Color) -> list[chess.Square]:
    """Squares of the opponent's pieces, the king excluded."""
    return _pieces_of(board, not colour)


def _our_sliders(board: chess.Board, colour: chess.Color):
    """``(square, piece_type)`` for every sliding piece of ``colour``."""
    return [
        (sq, piece.piece_type)
        for sq, piece in board.piece_map().items()
        if piece.color == colour and _ray_directions(piece.piece_type)
    ]


def _target_value(board: chess.Board, square: chess.Square) -> int:
    """Worth of a square as a *target*: the king is worth a queen, so forks on it count."""
    piece = board.piece_at(square)
    if piece is not None and piece.piece_type == chess.KING:
        return king_value_cp
    return piece_value(piece)


def _our_checkers(board: chess.Board, colour: chess.Color) -> list[chess.Square]:
    """Squares of ``colour``'s pieces attacking the enemy king in ``board``."""
    enemy_king = board.king(not colour)
    if enemy_king is None:
        return []
    return [
        sq for sq in chess.SquareSet(board.occupied_co[colour]) if enemy_king in board.attacks(sq)
    ]


@detector
def detect_fork(ctx: DetectionContext) -> ThemeHit | None:
    """The moved piece hits two or more worthwhile targets at once, and keeps its material.

    A fork that walks into the recapture ("forked it and lost it") is not a fork, so the move has
    to survive: its SEE gain may not fall below ``-FORK_MAX_SELF_LOSS_CP``.
    """
    if ctx.see.gain_cp < -FORK_MAX_SELF_LOSS_CP:
        return None

    enemy_king = ctx.after.king(ctx.opponent)
    candidates = _enemy_pieces(ctx.after, ctx.side) + (
        [enemy_king] if enemy_king is not None else []
    )
    targets = [
        sq
        for sq in candidates
        if _target_value(ctx.after, sq) >= FORK_MIN_TARGET_CP
        and sq in ctx.after.attacks(ctx.to_square)
    ]
    if len(targets) < 2:
        return None

    named = " and ".join(f"{ctx.pieces(ctx.after, sq)[0]}" for sq in targets)
    return ThemeHit(
        theme="fork",
        squares=ctx.squares(ctx.to_square, *targets),
        pieces=ctx.pieces(ctx.after, ctx.to_square),
        evidence=(
            f"{ctx.pieces(ctx.after, ctx.to_square)[0]} hits {named} at once and does not hang"
        ),
    )


@detector
def detect_pin(ctx: DetectionContext) -> ThemeHit | None:
    """An enemy piece is absolutely pinned, or held by a single cheaper attacker (relative pin)."""
    for sq in _enemy_pieces(ctx.after, ctx.side):
        if ctx.after.is_pinned(ctx.opponent, sq):
            label = ctx.pieces(ctx.after, sq)[0]
            return ThemeHit(
                theme="pin",
                squares=ctx.squares(sq),
                pieces=ctx.pieces(ctx.after, sq),
                evidence=f"{label} cannot move without exposing its own king",
            )

    # Relative pin: one cheaper attacker faces a defended piece, so it is not going to be taken
    # for free -- it pins the defender down by presence. A defenderless piece is hanging_piece.
    for sq in _enemy_pieces(ctx.after, ctx.side):
        target = piece_value(ctx.after.piece_at(sq))
        if target < HANGING_MIN_PIECE_CP:
            continue
        attackers = occupied_attackers(ctx.after, sq, ctx.side)
        if len(attackers) != 1:
            continue
        attacker = attackers[0]
        if piece_value(ctx.after.piece_at(attacker)) >= target:
            continue
        if not occupied_attackers(ctx.after, sq, ctx.opponent):
            continue
        return ThemeHit(
            theme="pin",
            confidence=0.6,
            squares=ctx.squares(sq),
            pieces=ctx.pieces(ctx.after, sq, attacker),
            evidence=(
                f"the cheap {ctx.pieces(ctx.after, attacker)[0]} holds the defended "
                f"{ctx.pieces(ctx.after, sq)[0]} in place"
            ),
        )
    return None


@detector
def detect_skewer(ctx: DetectionContext) -> ThemeHit | None:
    """A slider aims at a valuable front piece with something less valuable behind it.

    The front piece has to be the *more* valuable one: attacking it forces it aside and the rear
    piece falls. That value ordering is what keeps this disjoint from :func:`detect_x_ray`.
    """
    for square, piece_type in _our_sliders(ctx.after, ctx.side):
        for front, back in _two_piece_rays(ctx.after, square, piece_type):
            front_piece, back_piece = ctx.after.piece_at(front), ctx.after.piece_at(back)
            if front_piece is None or back_piece is None or front_piece.color == ctx.side:
                continue
            if back_piece.color == ctx.side:
                continue
            front_value, back_value = piece_value(front_piece), piece_value(back_piece)
            if front_value >= FORK_MIN_TARGET_CP and front_value > back_value > 0:
                return ThemeHit(
                    theme="skewer",
                    confidence=0.7,
                    squares=ctx.squares(square, front, back),
                    pieces=ctx.pieces(ctx.after, square),
                    evidence=(
                        f"{ctx.pieces(ctx.after, square)[0]} skewers the valuable "
                        f"{ctx.pieces(ctx.after, front)[0]}, which must step aside and let "
                        f"{ctx.pieces(ctx.after, back)[0]} fall"
                    ),
                )
    return None


def _opens_ray(ctx: DetectionContext, slider: chess.Square, through: chess.Square) -> bool:
    """Did *this move* put ``slider`` on the line, or vacate a square along it?

    Without this the x-ray rule reports every pre-existing x-ray anywhere on the board on every
    move, which is why it scored F1 0.00 against the puzzle tags: the motif is a property of the
    move, not of the position.
    """
    if slider == ctx.to_square:
        return True
    return bool(chess.BB_SQUARES[ctx.from_square] & chess.between(slider, through))


@detector
def detect_x_ray(ctx: DetectionContext) -> ThemeHit | None:
    """A slider sees a valuable piece *behind* a weaker one -- the mirror image of a skewer.

    Here the rear piece is the valuable one, so the front piece is worth giving up to get at
    it. Between this and :func:`detect_skewer`, both alignments of a two-piece ray are covered.

    The ray has to be *created by this move* -- either the moved piece is the slider, or the
    move vacated a square on the line. A pre-existing x-ray is somebody else's move, not this
    one's, and counting it made the detector useless (P 0.002 on the corpus before this change).
    """
    for square, piece_type in _our_sliders(ctx.after, ctx.side):
        for front, back in _two_piece_rays(ctx.after, square, piece_type):
            front_piece, back_piece = ctx.after.piece_at(front), ctx.after.piece_at(back)
            if front_piece is None or back_piece is None or front_piece.color == ctx.side:
                continue
            if back_piece.color == ctx.side:
                continue
            front_value, back_value = piece_value(front_piece), piece_value(back_piece)
            if back_value < FORK_MIN_TARGET_CP or back_value <= front_value:
                continue
            if not _opens_ray(ctx, square, back):
                continue
            return ThemeHit(
                theme="x_ray",
                confidence=0.6,
                squares=ctx.squares(square, front, back),
                pieces=ctx.pieces(ctx.after, square),
                evidence=(
                    f"{ctx.pieces(ctx.after, square)[0]} sees through "
                    f"{ctx.pieces(ctx.after, front)[0]} to the valuable "
                    f"{ctx.pieces(ctx.after, back)[0]} behind it"
                ),
            )
    return None


@detector
def detect_discovered_attack(ctx: DetectionContext) -> ThemeHit | None:
    """Vacating the from-square opens one of our sliders onto a worthwhile enemy piece."""
    vacated = ctx.from_square
    for square, piece_type in _our_sliders(ctx.after, ctx.side):
        for ray in _ray_occupants(ctx.after, square, piece_type):
            target = ray[0]
            piece = ctx.after.piece_at(target)
            if (
                piece is None
                or piece.color == ctx.side
                or piece_value(piece) < HANGING_MIN_PIECE_CP
            ):
                continue
            # The attack has to run *through* the vacated square and the vacated square has to be
            # strictly between -- otherwise the target was already attacked before the move.
            if not chess.BB_SQUARES[vacated] & chess.between(square, target):
                continue
            return ThemeHit(
                theme="discovered_attack",
                squares=ctx.squares(square, vacated, target),
                pieces=ctx.pieces(ctx.after, target),
                evidence=(
                    f"moving off {chess.square_name(vacated)} opens "
                    f"{ctx.pieces(ctx.after, square)[0]} onto {ctx.pieces(ctx.after, target)[0]}"
                ),
            )
    return None


@detector
def detect_discovered_check(ctx: DetectionContext) -> ThemeHit | None:
    """The check exists only because the from-square was vacated, and the mover does not check."""
    checkers = _our_checkers(ctx.after, ctx.side)
    if ctx.to_square in checkers:
        return (
            None  # the moved piece checks in its own right; that is a check, not a discovered one
        )
    if not checkers:
        return None
    checker = checkers[0]
    return ThemeHit(
        theme="discovered_check",
        squares=ctx.squares(ctx.from_square, checker),
        pieces=ctx.pieces(ctx.after, checker),
        evidence=(
            f"vacating {chess.square_name(ctx.from_square)} uncovers the check from "
            f"{ctx.pieces(ctx.after, checker)[0]}"
        ),
    )


@detector
def detect_double_check(ctx: DetectionContext) -> ThemeHit | None:
    """The moved piece checks *and* vacating its square uncovers a second check."""
    checkers = _our_checkers(ctx.after, ctx.side)
    if ctx.to_square not in checkers:
        return None
    others = [sq for sq in checkers if sq != ctx.to_square]
    if not others:
        return None
    other = others[0]
    return ThemeHit(
        theme="double_check",
        squares=ctx.squares(ctx.to_square, ctx.from_square, other),
        pieces=ctx.pieces(ctx.after, ctx.to_square, other),
        evidence=(
            f"{ctx.pieces(ctx.after, ctx.to_square)[0]} checks directly while the vacated square "
            f"uncovers {ctx.pieces(ctx.after, other)[0]}"
        ),
    )


@detector
def detect_hanging_piece(ctx: DetectionContext) -> ThemeHit | None:
    """The move leaves a worthwhile enemy piece attackable with a material gain.

    "Hanging" is taken literally: the piece must have **no defender at all**. Counting merely
    out-numbered pieces (attackers > defenders) made this fire on a large part of every corpus
    (F1 0.05) because a defended piece under two attackers is not what the tag means.
    """
    best: chess.Square | None = None
    for sq in _enemy_pieces(ctx.after, ctx.side):
        if piece_value(ctx.after.piece_at(sq)) < HANGING_MIN_PIECE_CP:
            continue
        gain = net_attackers(ctx.after, sq, ctx.side)
        if gain < HANGING_PIECE_MIN_NET_ATTACKERS:
            continue
        if occupied_attackers(ctx.after, sq, ctx.opponent):
            continue  # defended: under pressure, but not hanging
        # Only report what *this* move exposed: either the moved piece attacks it, or the move
        # added an attacker. A piece that was already loose is somebody else's mistake.
        is_new = sq in ctx.after.attacks(ctx.to_square) or gain > net_attackers(
            ctx.board, sq, ctx.side
        )
        if is_new and (
            best is None
            or piece_value(ctx.after.piece_at(sq)) > piece_value(ctx.after.piece_at(best))
        ):
            best = sq
    if best is None:
        return None
    return ThemeHit(
        theme="hanging_piece",
        squares=ctx.squares(best),
        pieces=ctx.pieces(ctx.after, best),
        evidence=(
            f"{ctx.pieces(ctx.after, best)[0]} is left hanging, undefended and attacked "
            f"{net_attackers(ctx.after, best, ctx.side)} time(s)"
        ),
    )


@detector
def detect_hanging_piece_defended(ctx: DetectionContext) -> ThemeHit | None:
    """The move saves one of our own pieces that was genuinely hanging before it."""
    for sq, piece in ctx.board.piece_map().items():
        if piece.color != ctx.side or piece_value(piece) < HANGING_MIN_PIECE_CP:
            continue
        if ctx.after.piece_at(sq) is None:
            continue  # it walked away -- that is a retreat, not a defence
        was = net_attackers(ctx.board, sq, ctx.opponent)
        now = net_attackers(ctx.after, sq, ctx.opponent)
        if was < HANGING_PIECE_MIN_NET_ATTACKERS or now >= was:
            continue
        return ThemeHit(
            theme="hanging_piece_defended",
            squares=ctx.squares(sq, ctx.to_square),
            pieces=ctx.pieces(ctx.after, sq, ctx.to_square),
            evidence=(
                f"{ctx.pieces(ctx.after, sq)[0]} was hanging and is now covered by "
                f"{ctx.pieces(ctx.after, ctx.to_square)[0]}"
            ),
        )
    return None


@detector
def detect_threat_created(ctx: DetectionContext) -> ThemeHit | None:
    """The move attacks a worthwhile enemy piece that is defended -- a threat, not a freebie.

    This is the complement of :func:`detect_hanging_piece`: same target, opposite net count.
    A piece that is attacked but even is something the opponent has to *do* something about.
    """
    best: chess.Square | None = None
    for sq in _enemy_pieces(ctx.after, ctx.side):
        if piece_value(ctx.after.piece_at(sq)) < HANGING_MIN_PIECE_CP:
            continue
        if net_attackers(ctx.after, sq, ctx.side) >= HANGING_PIECE_MIN_NET_ATTACKERS:
            continue  # that is hanging_piece
        if not occupied_attackers(ctx.after, sq, ctx.side):
            continue
        is_new = sq in ctx.after.attacks(ctx.to_square) or not occupied_attackers(
            ctx.board, sq, ctx.side
        )
        if is_new and (
            best is None
            or piece_value(ctx.after.piece_at(sq)) > piece_value(ctx.after.piece_at(best))
        ):
            best = sq
    if best is None:
        return None
    return ThemeHit(
        theme="threat_created",
        confidence=0.8,
        squares=ctx.squares(best),
        pieces=ctx.pieces(ctx.after, best, ctx.to_square),
        evidence=f"the move now attacks the defended {ctx.pieces(ctx.after, best)[0]}",
    )


@detector
def detect_back_rank_mate(ctx: DetectionContext) -> ThemeHit | None:
    """Checkmate delivered to a king that never left its own back rank."""
    if not ctx.is_mate:
        return None
    enemy_king = ctx.after.king(ctx.opponent)
    back_rank = 0 if ctx.opponent == chess.WHITE else 7
    if chess.square_rank(enemy_king) != back_rank:
        return None
    return ThemeHit(
        theme="back_rank_mate",
        squares=ctx.squares(ctx.to_square, enemy_king),
        pieces=ctx.pieces(ctx.after, ctx.to_square),
        evidence=(
            f"{ctx.san()} mates: the king on {chess.square_name(enemy_king)} never left its back "
            f"rank"
        ),
    )


@detector
def detect_trapped_piece(ctx: DetectionContext) -> ThemeHit | None:
    """An enemy piece we are attacking has no square it can step to that stays safe."""
    best: chess.Square | None = None
    for sq in _enemy_pieces(ctx.after, ctx.side):
        if piece_value(ctx.after.piece_at(sq)) < HANGING_MIN_PIECE_CP or not occupied_attackers(
            ctx.after, sq, ctx.side
        ):
            continue
        replies = list(ctx.after.generate_legal_moves(from_mask=chess.BB_SQUARES[sq]))
        escapes = [
            reply.to_square
            for reply in replies
            if not occupied_attackers(ctx.after, reply.to_square, ctx.side)
        ]
        more_valuable = best is None or piece_value(ctx.after.piece_at(sq)) > piece_value(
            ctx.after.piece_at(best)
        )
        if replies and not escapes and more_valuable:
            best = sq
    if best is None:
        return None
    return ThemeHit(
        theme="trapped_piece",
        confidence=0.7,
        squares=ctx.squares(best),
        pieces=ctx.pieces(ctx.after, best),
        evidence=(
            f"{ctx.pieces(ctx.after, best)[0]} is attacked and every square it can reach is "
            f"covered too"
        ),
    )


@detector
def detect_overloaded_defender(ctx: DetectionContext) -> ThemeHit | None:
    """An enemy piece is the sole defender of two different pieces we both attack.

    It cannot save both at once: if it stays, one of them falls; if it moves, the other
    does. That "one piece, two jobs" split is the overload.
    """
    for guard in _enemy_pieces(ctx.after, ctx.side):
        guarded = [
            target
            for target in _enemy_pieces(ctx.after, ctx.side)
            if target != guard
            and ctx.after.attackers_mask(ctx.opponent, target) == chess.BB_SQUARES[guard]
            and occupied_attackers(ctx.after, target, ctx.side)
        ]
        if len(guarded) >= 2:
            first, second = guarded[0], guarded[1]
            return ThemeHit(
                theme="overloaded_defender",
                confidence=0.6,
                squares=ctx.squares(guard, first, second),
                pieces=ctx.pieces(ctx.after, guard),
                evidence=(
                    f"{ctx.pieces(ctx.after, guard)[0]} is the only defender of both "
                    f"{ctx.pieces(ctx.after, first)[0]} and {ctx.pieces(ctx.after, second)[0]}"
                ),
            )
    return None


@detector
def detect_deflection(ctx: DetectionContext) -> ThemeHit | None:
    """We attack a piece *and* the piece that is the only thing guarding another attacked piece.

    That is the deflection proper: the guard has to choose between its two jobs. Attacking a
    piece simply because it happens to be the only attacker of one of ours is not this theme --
    it is just an ordinary capture of an attacker.
    """
    under_our_eyes = [
        target
        for target in _enemy_pieces(ctx.after, ctx.side)
        if occupied_attackers(ctx.after, target, ctx.side)
    ]
    for guard in _enemy_pieces(ctx.after, ctx.side):
        if guard not in ctx.after.attacks(ctx.to_square):
            continue  # the move is not going after the guard
        for target in under_our_eyes:
            if ctx.after.attackers_mask(ctx.opponent, target) != chess.BB_SQUARES[guard]:
                continue  # not its only remaining defender
            return ThemeHit(
                theme="deflection",
                confidence=0.6,
                squares=ctx.squares(guard, target, ctx.to_square),
                pieces=ctx.pieces(ctx.after, guard, target),
                evidence=(
                    f"going after {ctx.pieces(ctx.after, guard)[0]} drags the only defender off "
                    f"{ctx.pieces(ctx.after, target)[0]}, which is under attack anyway"
                ),
            )
    return None


@detector
def detect_interference(ctx: DetectionContext) -> ThemeHit | None:
    """The moved piece stepped into an enemy slider's line, denying it a capture it had.

    Checked by comparing the same ray in both positions: if the first thing the slider met
    before the move was one of our pieces and the first thing it meets now is the piece we just
    moved, then our move is exactly what interposed.

    The shielded piece must also have been **genuinely threatened** before the move (or be the
    king, i.e. the move blocks a check). Requiring only "the move landed on the line" made this
    fire on a large share of all moves -- landing on some enemy slider's path by accident is
    common -- and it scored F1 0.002 on the corpus.
    """
    blocker = ctx.after.piece_at(ctx.to_square)
    if blocker is None or blocker.color != ctx.side:
        return None
    for square, piece_type in _our_sliders(ctx.after, ctx.opponent):
        for df, dr in _ray_directions(piece_type):
            first_after = _first_on_ray(ctx.after, square, df, dr)
            if first_after != ctx.to_square:
                continue
            first_before = _first_on_ray(ctx.board, square, df, dr)
            if first_before is None or first_before == ctx.to_square:
                continue
            target = ctx.board.piece_at(first_before)
            if target is None or target.color != ctx.side:
                continue  # the slider was aiming at empty space, not at a capture
            if target.piece_type != chess.KING and (
                net_attackers(ctx.board, first_before, ctx.opponent)
                < HANGING_PIECE_MIN_NET_ATTACKERS
            ):
                continue  # nothing was actually threatened, so the block accomplishes nothing
            return ThemeHit(
                theme="interference",
                confidence=0.7,
                squares=ctx.squares(square, ctx.to_square, first_before),
                pieces=ctx.pieces(ctx.after, square, ctx.to_square),
                evidence=(
                    f"{ctx.pieces(ctx.after, ctx.to_square)[0]} interposes on the "
                    f"{ctx.pieces(ctx.after, square)[0]}'s line, denying the capture on "
                    f"{chess.square_name(first_before)}"
                ),
            )
    return None


def _first_on_ray(
    board: chess.Board, origin: chess.Square, df: int, dr: int
) -> chess.Square | None:
    """First occupied square along one step direction from ``origin``."""
    f, r = chess.square_file(origin) + df, chess.square_rank(origin) + dr
    while 0 <= f < 8 and 0 <= r < 8:
        square = chess.square(f, r)
        if board.piece_at(square):
            return square
        f += df
        r += dr
    return None
