"""Intent tags: a plausible *why* for the move, on top of the ``theme`` facts.

Intent is deliberately less exact than the theme layer. A theme is something a human can
verify on the board ("this is a fork"); an intent is a plausible *purpose* ("this move
develops a piece", "this move creates a threat"). Every tag is therefore a rule with an
evidence string, never a bare boolean, and the engine-backed tags are optional and
flag-controlled because they cost extra search.

Two kinds of intent:

* **Static** tags (``develops``, ``castles``, ``simplifies``, ``attacks_king``,
  ``improves_piece``, ``restricts_opponent``, ``defends_material``, ``prepares_break``,
  ``trades_defender``) -- decided from the two positions and the already-computed theme
  hits and SEE. Free to evaluate.
* **Threat** tags (``creates_threat``, ``parries_threat``) -- decided by null-move engine
  probes, so they are *not* detectors in the registry; they are produced by
  :func:`threat_probe`, which the pipeline calls only when asked.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import chess

from ...config import INTENT_VOCAB, NULL_MOVE_THREAT_WP_JUMP
from ...schema import IntentTagModel
from ..features import FeatureSnapshot, centre_distance, snapshot
from ..see import SeeResult
from .base import DetectionContext, ThemeHit

if TYPE_CHECKING:  # pragma: no cover - import only for the type hints
    from ...engine.client import AnalysisLimit, StockfishClient

__all__ = [
    "ENGINE_INTENT_TAGS",
    "INTENT_REGISTRY",
    "IntentContext",
    "IntentTag",
    "detect_intents",
    "intent_detector",
    "registered_intents",
    "threat_probe",
]

#: The intent tags that need an engine probe and are therefore *not* in the static
#: registry; produced by :func:`threat_probe`. Together with the registry they cover
#: :data:`moveexp.config.INTENT_VOCAB` exactly.
ENGINE_INTENT_TAGS: tuple[str, ...] = ("creates_threat", "parries_threat")

_INTENT_ORDER: dict[str, int] = {tag: index for index, tag in enumerate(INTENT_VOCAB)}


def _validate_tag(tag: str) -> str:
    if tag not in _INTENT_ORDER:
        raise ValueError(f"{tag!r} is not in INTENT_VOCAB")
    return tag


@dataclass(frozen=True)
class IntentTag:
    """One intent, with the evidence and the moves that justify it."""

    tag: str
    evidence: str = ""
    moves: tuple[str, ...] = ()
    confidence: float = 1.0

    def __post_init__(self) -> None:
        _validate_tag(self.tag)
        if not self.evidence:
            raise ValueError(f"intent {self.tag!r} was reported without evidence")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be in [0, 1], got {self.confidence}")

    def to_model(self) -> IntentTagModel:
        """Serialise for :class:`moveexp.schema.MoveReport`."""
        return IntentTagModel(
            tag=self.tag,
            evidence=self.evidence,
            moves=list(self.moves),
            confidence=self.confidence,
        )

    def sort_key(self) -> tuple[int, str]:
        return (_INTENT_ORDER[self.tag], self.evidence)


@dataclass(frozen=True)
class IntentContext:
    """What the static intent detectors read: the two positions, SEE, features and themes."""

    board: chess.Board
    move: chess.Move
    after: chess.Board
    side: chess.Color
    see: SeeResult
    features_before: FeatureSnapshot
    features_after: FeatureSnapshot
    themes: tuple[ThemeHit, ...] = ()

    @classmethod
    def from_detection(
        cls, ctx: DetectionContext, themes: tuple[ThemeHit, ...] | list[ThemeHit] = ()
    ) -> IntentContext:
        return cls(
            board=ctx.board,
            move=ctx.move,
            after=ctx.after,
            side=ctx.side,
            see=ctx.see,
            features_before=ctx.features_before,
            features_after=ctx.features_after,
            themes=tuple(themes),
        )

    @property
    def opponent(self) -> chess.Color:
        return not self.side

    @property
    def to_square(self) -> chess.Square:
        return self.move.to_square

    @property
    def from_square(self) -> chess.Square:
        return self.move.from_square

    @property
    def moved_piece(self) -> chess.Piece | None:
        return self.board.piece_at(self.move.from_square)

    @property
    def is_capture(self) -> bool:
        return self.board.is_capture(self.move)

    @property
    def is_castling(self) -> bool:
        return self.board.is_castling(self.move)

    def has_theme(self, theme: str) -> bool:
        return any(hit.theme == theme for hit in self.themes)

    def san(self) -> str:
        return self.board.san(self.move)


#: Registered static intent detectors, in registration order.
INTENT_REGISTRY: list = []


def intent_detector(func):
    """Register a static intent detector and return it unchanged."""
    if func.__name__ in {existing.__name__ for existing in INTENT_REGISTRY}:
        raise ValueError(f"an intent detector named {func.__name__!r} is already registered")
    INTENT_REGISTRY.append(func)
    return func


def registered_intents() -> tuple:
    return tuple(INTENT_REGISTRY)


def detect_intents(ctx: IntentContext) -> list[IntentTag]:
    """Run every static intent detector over ``ctx``, deduplicated and sorted."""
    seen: dict[tuple[object, ...], IntentTag] = {}
    for func in INTENT_REGISTRY:
        result = func(ctx)
        if result is None:
            continue
        for tag in result if isinstance(result, (list, tuple)) else [result]:
            seen.setdefault((tag.tag, tag.evidence, tag.moves), tag)
    return sorted(seen.values(), key=IntentTag.sort_key)


# ---------------------------------------------------------------------- static detectors
def _enemy_pieces(board: chess.Board, side: chess.Color) -> list[chess.Square]:
    mask = board.occupied_co[not side] & ~board.kings
    return list(chess.SquareSet(mask))


@intent_detector
def _develops(ctx: IntentContext) -> IntentTag | None:
    piece = ctx.moved_piece
    if piece is None or piece.piece_type in (chess.PAWN, chess.KING, chess.QUEEN):
        return None
    home_rank = 0 if ctx.side == chess.WHITE else 7
    from_rank = chess.square_rank(ctx.from_square)
    to_rank = chess.square_rank(ctx.to_square)
    advanced = to_rank > from_rank if ctx.side == chess.WHITE else to_rank < from_rank
    if from_rank != home_rank or not advanced:
        return None
    return IntentTag(
        "develops",
        evidence=f"develops the {piece.symbol()} to {chess.square_name(ctx.to_square)}",
    )


@intent_detector
def _castles(ctx: IntentContext) -> IntentTag | None:
    if not ctx.is_castling:
        return None
    return IntentTag("castles", evidence="the move castles")


@intent_detector
def _simplifies(ctx: IntentContext) -> IntentTag | None:
    if not ctx.is_capture or not ctx.see.is_even:
        return None
    return IntentTag("simplifies", evidence="an even exchange that thins the position")


@intent_detector
def _attacks_king(ctx: IntentContext) -> IntentTag | None:
    if ctx.after.is_check():
        return IntentTag("attacks_king", evidence=f"{ctx.san()} gives check")
    if ctx.has_theme("weakens_opponent_king"):
        return IntentTag(
            "attacks_king", confidence=0.7, evidence="pressure on the enemy king rises"
        )
    return None


@intent_detector
def _improves_piece(ctx: IntentContext) -> IntentTag | None:
    piece = ctx.moved_piece
    if piece is None or piece.piece_type in (chess.PAWN, chess.KING):
        return None
    if centre_distance(ctx.to_square) >= centre_distance(ctx.from_square):
        return None
    return IntentTag(
        "improves_piece",
        confidence=0.7,
        evidence=f"the {piece.symbol()} moves toward the centre",
    )


@intent_detector
def _restricts_opponent(ctx: IntentContext) -> IntentTag | None:
    before = snapshot(ctx.board, ctx.opponent).mobility
    after = snapshot(ctx.after, ctx.opponent).mobility
    if after >= before:
        return None
    return IntentTag(
        "restricts_opponent",
        confidence=0.7,
        evidence=f"opponent mobility drops from {before:.1f} to {after:.1f}",
    )


@intent_detector
def _defends_material(ctx: IntentContext) -> IntentTag | None:
    if not ctx.has_theme("hanging_piece_defended"):
        return None
    return IntentTag("defends_material", evidence="the move covers an attacked piece")


@intent_detector
def _prepares_break(ctx: IntentContext) -> IntentTag | None:
    piece = ctx.moved_piece
    if piece is None or piece.piece_type != chess.PAWN or ctx.is_capture:
        return None
    rank = chess.square_rank(ctx.to_square)
    file = chess.square_file(ctx.to_square)
    for df in (-1, 1):
        f = file + df
        if not 0 <= f < 8:
            continue
        target = ctx.after.piece_at(chess.square(f, rank))
        if target is not None and target.piece_type == chess.PAWN and target.color == ctx.opponent:
            return IntentTag(
                "prepares_break",
                evidence=(
                    f"pawn on {chess.square_name(ctx.to_square)} faces the enemy pawn on "
                    f"{chess.square_name(chess.square(f, rank))}"
                ),
            )
    return None


@intent_detector
def _trades_defender(ctx: IntentContext) -> IntentTag | None:
    if not ctx.is_capture:
        return None
    captured_square = ctx.to_square
    for target in _enemy_pieces(ctx.after, ctx.side):
        was_defender = (
            ctx.board.attackers_mask(ctx.opponent, target) & chess.BB_SQUARES[captured_square]
        )
        we_attack_target = (
            ctx.after.attackers_mask(ctx.side, target) & ctx.after.occupied_co[ctx.side]
        )
        if was_defender and we_attack_target:
            return IntentTag(
                "trades_defender",
                confidence=0.7,
                evidence=f"the move removes the defender of {chess.square_name(target)}",
            )
    return None


# ------------------------------------------------------------------- engine threat probe
def threat_probe(
    client: StockfishClient,
    board_before: chess.Board,
    move: chess.Move,
    limit: AnalysisLimit,
    *,
    jump: float = NULL_MOVE_THREAT_WP_JUMP,
) -> list[IntentTag]:
    """Null-move threat test: does the move create a threat, or parry one that existed?

    Cost: up to four extra single-PV searches per position. The caller should run this only
    on flagged positions and at a reduced budget (see the README "Cost model").

    A "null move" is simulated by flipping the side to move, so the mover (or the opponent)
    gets a free extra move; a large jump in that side's win probability means it has a real
    threat. Positions where the side to move is in check are skipped, because there the
    threat is the check itself, not something a probe needs to discover.
    """
    from ...engine.eval_utils import line_win_prob

    mover = board_before.turn
    opponent = not mover
    board_after = board_before.copy(stack=False)
    board_after.push(move)
    tags: list[IntentTag] = []

    def _wp(board: chess.Board, side_to_move: chess.Color) -> float | None:
        """Win probability of ``side_to_move``'s best line, or ``None`` if not measurable."""
        probe = board.copy(stack=False)
        probe.turn = side_to_move
        if probe.is_check() or probe.is_game_over():
            return None
        try:
            lines = client.analyse(probe, limit, multipv=1)
        except Exception:  # a null-move position is approximate; never fail the whole run
            return None
        return line_win_prob(lines[0]) if lines else None

    # creates_threat: after the move, the mover gains a lot from a free extra move.
    opponent_wp = _wp(board_after, opponent)  # None if the opponent is in check
    mover_free_wp = _wp(board_after, mover)
    if (
        opponent_wp is not None
        and mover_free_wp is not None
        and mover_free_wp - (1.0 - opponent_wp) > jump
    ):
        tags.append(
            IntentTag(
                "creates_threat",
                confidence=0.8,
                moves=(move.uci(),),
                evidence="after the move the engine, moving again, finds a big gain",
            )
        )

    # parries_threat: the opponent had a real threat before, and the move holds the position.
    mover_before_wp = _wp(board_before, mover)
    opponent_free_wp = _wp(board_before, opponent)
    if mover_before_wp is not None and opponent_free_wp is not None and opponent_wp is not None:
        had_threat = mover_before_wp - (1.0 - opponent_free_wp) > jump
        mover_after_wp = 1.0 - opponent_wp
        if had_threat and mover_after_wp >= mover_before_wp:
            tags.append(
                IntentTag(
                    "parries_threat",
                    confidence=0.7,
                    moves=(move.uci(),),
                    evidence="the move removes the threat the opponent had before",
                )
            )

    return tags
