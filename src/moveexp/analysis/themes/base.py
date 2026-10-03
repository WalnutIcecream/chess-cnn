"""What every theme detector shares: the hit record, the context, and the registry.

A detector is a pure function from a :class:`DetectionContext` to zero or more
:class:`ThemeHit` records. Nothing else is required of it: no engine, no cache, no I/O, no
knowledge of the other detectors. That keeps detectors individually testable and lets the
whole layer be run in any order.

Two rules make the layer debuggable, which matters because its output is what an LLM is
asked to explain:

* **The vocabulary is enforced at construction time.** A hit whose theme is not in
  :data:`moveexp.config.THEME_VOCAB` raises immediately, so a typo in a detector is a test
  failure with a traceback instead of a silently missing explanation.
* **Every hit carries its own evidence.** The one-line justification is written next to the
  rule that produced it and is shipped verbatim in the report, so a wrong explanation can be
  traced back to a specific detector without re-running anything.

Naming convention used in the ``pieces`` field: ``"N@f5"`` is a white knight, ``"n@f5"`` a
black one -- the same upper/lower-case rule as FEN.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass

import chess

from ...config import THEME_VOCAB
from ...schema import ThemeHitModel
from ..features import FeatureSnapshot, snapshot
from ..see import SeeResult, see_after_move

__all__ = [
    "DetectionContext",
    "Detector",
    "DetectorReport",
    "HitResult",
    "REGISTRY",
    "ThemeHit",
    "detect",
    "detector",
    "iter_themes",
    "piece_label",
    "registered_detectors",
    "run_all",
    "theme_order",
    "validate_theme",
]

_THEME_ORDER: dict[str, int] = {name: index for index, name in enumerate(THEME_VOCAB)}


def validate_theme(theme: str) -> str:
    """Return ``theme`` unchanged, or raise if it is not part of the frozen vocabulary."""
    if theme not in _THEME_ORDER:
        raise ValueError(f"{theme!r} is not in THEME_VOCAB")
    return theme


def theme_order(theme: str) -> int:
    """Position of ``theme`` in the vocabulary; used to sort reports deterministically."""
    return _THEME_ORDER[validate_theme(theme)]


def piece_label(board: chess.Board, square: chess.Square) -> str:
    """``"N@f5"`` for a white knight, ``"n@f5"`` for a black one, ``"@f5"`` when empty."""
    piece = board.piece_at(square)
    if piece is None:
        return f"@{chess.square_name(square)}"
    return f"{piece.symbol()}{'@'}{chess.square_name(square)}"


@dataclass(frozen=True)
class ThemeHit:
    """One rule matched, with everything needed to explain and audit it."""

    theme: str
    squares: tuple[str, ...] = ()
    pieces: tuple[str, ...] = ()
    confidence: float = 1.0
    evidence: str = ""

    def __post_init__(self) -> None:
        validate_theme(self.theme)
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be in [0, 1], got {self.confidence}")
        if not self.evidence:
            raise ValueError(f"theme {self.theme!r} was reported without evidence")

    def to_model(self) -> ThemeHitModel:
        """Serialise for :class:`moveexp.schema.MoveReport`."""
        return ThemeHitModel(
            theme=self.theme,
            squares=list(self.squares),
            pieces=list(self.pieces),
            confidence=self.confidence,
            evidence=self.evidence,
        )

    def sort_key(self) -> tuple[int, str, str]:
        """Vocabulary order first, so reports read the same way every time."""
        return (theme_order(self.theme), self.squares[0] if self.squares else "", self.evidence)


@dataclass(frozen=True)
class DetectionContext:
    """Everything a detector may need, computed once per move.

    Building this is the only place that knows the sequence "before -> play -> after"; every
    detector receives the result and only reads. The feature snapshots and the SEE result are
    included because most detectors would otherwise recompute them per rule, and because two
    detectors answering the same question must get the same answer.
    """

    board: chess.Board
    """Position **before** the move."""

    move: chess.Move
    side: chess.Color
    """Side that played the move; ``board.turn`` by construction."""

    after: chess.Board
    """Position **after** the move, with the opponent to move."""

    see: SeeResult
    features_before: FeatureSnapshot
    features_after: FeatureSnapshot

    @classmethod
    def from_move(cls, board: chess.Board, move: chess.Move) -> DetectionContext:
        """Play ``move`` on a copy and collect everything the detectors read.

        :raises ValueError: if ``move`` is not legal in ``board``.
        """
        if move not in board.legal_moves:
            raise ValueError(f"{board.uci(move)} is not legal in {board.fen()}")
        after = board.copy(stack=False)
        after.push(move)
        side = board.turn
        return cls(
            board=board,
            move=move,
            side=side,
            after=after,
            see=see_after_move(board, move),
            features_before=snapshot(board, side),
            features_after=snapshot(after, side),
        )

    # -- convenience readers, so detectors stay free of board plumbing --------------------
    @property
    def opponent(self) -> chess.Color:
        return not self.side

    @property
    def from_square(self) -> chess.Square:
        return self.move.from_square

    @property
    def to_square(self) -> chess.Square:
        return self.move.to_square

    @property
    def moved_piece(self) -> chess.Piece | None:
        """The piece that made the move, as it stands in the position *before* it."""
        return self.board.piece_at(self.move.from_square)

    @property
    def moved_piece_after(self) -> chess.Piece | None:
        """The moved piece on its new square (a pawn that promoted comes back as a queen)."""
        return self.after.piece_at(self.move.to_square)

    @property
    def captured(self) -> chess.Piece | None:
        """The captured piece; ``None`` for a quiet move or en passant (see :attr:`is_ep`)."""
        if self.board.is_en_passant(self.move):
            return chess.Piece(chess.PAWN, self.opponent)
        return self.board.piece_at(self.move.to_square)

    @property
    def is_capture(self) -> bool:
        return self.board.is_capture(self.move)

    @property
    def is_ep(self) -> bool:
        return self.board.is_en_passant(self.move)

    @property
    def is_castling(self) -> bool:
        return self.board.is_castling(self.move)

    @property
    def is_promotion(self) -> bool:
        return self.move.promotion is not None

    @property
    def is_check(self) -> bool:
        return self.after.is_check()

    @property
    def is_mate(self) -> bool:
        return self.after.is_checkmate()

    def san(self) -> str:
        """SAN of the move, in the position before it."""
        return self.board.san(self.move)

    def uci(self) -> str:
        return self.board.uci(self.move)

    def squares(self, *squares: chess.Square) -> tuple[str, ...]:
        """Algebraic names for a detector's ``squares`` field."""
        return tuple(chess.square_name(square) for square in squares)

    def pieces(self, board: chess.Board | None, *squares: chess.Square) -> tuple[str, ...]:
        """Piece labels for a detector's ``pieces`` field; ``board`` defaults to the position
        before the move (pass ``ctx.after`` for where the pieces ended up)."""
        source = self.board if board is None else board
        return tuple(piece_label(source, square) for square in squares)


#: What a detector may return: nothing, one hit, or several. Most rules decide a single
#: verdict ("this is a fork" / "this is not"), so returning one hit or ``None`` is the
#: convenient default and only the rules that can fire more than once build a list.
HitResult = ThemeHit | Iterable[ThemeHit] | None

Detector = Callable[[DetectionContext], HitResult]

#: Every registered detector, in registration order.
REGISTRY: list[Detector] = []


def detector(func: Detector) -> Detector:
    """Register a detector function and return it unchanged.

    Used as a decorator::

        @detector
        def detect_fork(ctx: DetectionContext) -> Iterable[ThemeHit]:
            ...
    """
    if func.__name__ in {existing.__name__ for existing in REGISTRY}:
        raise ValueError(f"a detector named {func.__name__!r} is already registered")
    REGISTRY.append(func)
    return func


def _as_hits(result: HitResult) -> list[ThemeHit]:
    """Accept the three shapes a detector may return and flatten them to a list."""
    if result is None:
        return []
    if isinstance(result, ThemeHit):
        return [result]
    return list(result)


def registered_detectors() -> tuple[Detector, ...]:
    """The registered detectors, as an immutable snapshot."""
    return tuple(REGISTRY)


def run_all(ctx: DetectionContext, detectors: Sequence[Detector] | None = None) -> list[ThemeHit]:
    """Run every detector over ``ctx`` and return the hits in report order.

    Exact duplicates are dropped: two rules may legitimately reach the same conclusion (a
    capture that is also a trade), but they may not report it twice with identical evidence.
    """
    hits: list[ThemeHit] = []
    for func in detectors if detectors is not None else REGISTRY:
        hits.extend(_as_hits(func(ctx)))
    unique: dict[tuple[object, ...], ThemeHit] = {}
    for hit in hits:
        unique.setdefault((hit.theme, hit.squares, hit.pieces, hit.evidence), hit)
    return sorted(unique.values(), key=ThemeHit.sort_key)


def detect(board: chess.Board, move: chess.Move) -> list[ThemeHit]:
    """Build the context for ``move`` and run the whole theme layer over it."""
    return run_all(DetectionContext.from_move(board, move))


def iter_themes(hits: Iterable[ThemeHit]) -> Iterator[str]:
    """Theme names of ``hits``, in order -- handy for tests and for label summaries."""
    return (hit.theme for hit in hits)


@dataclass(frozen=True)
class DetectorReport:
    """Hits grouped by theme, for callers that care about one theme at a time."""

    hits: tuple[ThemeHit, ...] = ()

    def of(self, theme: str) -> tuple[ThemeHit, ...]:
        validate_theme(theme)
        return tuple(hit for hit in self.hits if hit.theme == theme)

    def has(self, theme: str) -> bool:
        return bool(self.of(theme))

    def themes(self) -> tuple[str, ...]:
        return tuple(sorted({hit.theme for hit in self.hits}, key=theme_order))
