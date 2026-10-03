"""Pydantic models that define every artefact this project writes.

This module is deliberately dependency-light (``pydantic`` only) so that the engine
layer, the theme detectors and the dataset writers can all import it without cycles:
``schema`` is the bottom of the dependency graph.

Naming note: the detector-side records are plain dataclasses that live next to the code
that produces them (``themes.base.ThemeHit``, ``themes.intent.IntentTag``). The classes
here are the *serialised* forms and are suffixed ``Model`` where that would otherwise
be ambiguous.

FEN conventions (used for identity, dedupe and cache keys)
----------------------------------------------------------
A *normalised* FEN is ``<board> <castling> <ep>`` -- the first four fields of a FEN with
the halfmove clock and the fullmove number removed. Two positions with the same
normalised FEN are treated as the same position. This matches the Lichess evaluation
database, which stores FENs without counters.

Caveat, stated explicitly: the halfmove clock (50-move rule) and the *legal-ness* of the
en-passant square are dropped. That is deliberate -- including the halfmove clock in the
key would make the cache useless -- but it means two positions that differ only in the
50-move counter share a cache entry. Positions that differ only in whether an en-passant
capture is pseudo-legal also share one; for cache purposes that is a small, bounded
error, and ``normalise_fen`` has a strict variant for the dataset keys.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from typing import Any, Final

import chess
from pydantic import BaseModel, ConfigDict, Field

from .config import (
    DATASET_VERSION,
    INTENT_VOCAB,
    QUALITY_LABELS,
    THEME_VOCAB,
)

# --------------------------------------------------------------------------------------
# FEN helpers
# --------------------------------------------------------------------------------------


def split_fen(fen: str) -> tuple[str, str, str, str, str, str]:
    """Split a FEN into its six fields.

    :param fen: a full or partial FEN string.
    :returns: ``(placement, side, castling, en_passant, halfmove, fullmove)``. Missing
        trailing fields are returned as ``"0"`` / ``"1"`` defaults so that partial FENs
        (as found in some corpora) can be normalised.
    """
    parts = fen.split()
    parts += ["-", "-", "0", "1"][max(0, 4 - len(parts)) :]
    placement, side, castling, ep = parts[0], parts[1], parts[2], parts[3]
    halfmove = parts[4] if len(parts) > 4 else "0"
    fullmove = parts[5] if len(parts) > 5 else "1"
    return placement, side, castling, ep, halfmove, fullmove


def normalise_fen(fen: str | chess.Board) -> str:
    """Return the move-counter-free form of ``fen``, used as position identity.

    >>> normalise_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -'
    """
    if isinstance(fen, chess.Board):
        fen = fen.fen()
    placement, side, castling, ep, _halfmove, _fullmove = split_fen(fen)
    return f"{placement} {side} {castling} {ep}"


# --------------------------------------------------------------------------------------
# Engine output
# --------------------------------------------------------------------------------------


class LineInfo(BaseModel):
    """One principal variation from a MultiPV search.

    Perspective rule: ``score_cp`` and ``mate`` are relative to ``turn``, the side to
    move of the *analysed* position. ``turn`` is stored explicitly so that no consumer
    has to remember which position a line came from; the single sanctioned conversion to
    another point of view is :func:`moveexp.engine.eval_utils.to_mover_perspective`.
    """

    model_config = ConfigDict(validate_assignment=True)

    turn: chess.Color
    """Side to move of the analysed position; every score here is relative to it."""

    move: str | None = None
    """UCI of the first move of the line (``None`` for an empty PV)."""

    pv: list[str] = Field(default_factory=list)
    """UCI moves of the principal variation."""

    score_cp: float | None = None
    """Centi-pawn score relative to :attr:`turn`. ``None`` when the score is a mate
    score that was not folded into centipawns (see :func:`eval_utils.mate_to_cp`)."""

    mate: int | None = None
    """Raw mate distance relative to :attr:`turn`: positive = :attr:`turn` mates in
    ``abs(mate)``, negative = :attr:`turn` is mated. Kept separate from ``score_cp`` so
    reports can say "mate in 3" instead of "+9997"."""

    depth: int = 0
    """Search depth actually reached."""

    seldepth: int | None = None
    """Selective depth, when the engine reports it."""

    nodes: int = 0
    """Nodes searched for this line (the engine reports the root total)."""

    multipv_rank: int = 1
    """1-based rank of this line inside the MultiPV set, as reported by the engine."""

    bound: str | None = None
    """``"upper"`` / ``"lower"`` for aspiration-window results. Lower bounds are
    optimistic and would corrupt rank ordering, so quality code skips them."""

    @property
    def is_mate(self) -> bool:
        """Whether the engine reports a forced mate for this line."""
        return self.mate is not None


class QualityInfo(BaseModel):
    """Move-quality and criticality numbers for one played move (Section 7).

    All evaluations are in the **mover's** point of view: positive means the position
    got better for the player who played the move.
    """

    model_config = ConfigDict(validate_assignment=True)

    label: str
    """One of ``config.QUALITY_LABELS``."""

    eval_before_cp: float
    """Centi-pawn evaluation of the position before the move (mover's POV)."""

    eval_after_cp: float
    """Centi-pawn evaluation of the position after the move (mover's POV)."""

    win_prob_before: float
    win_prob_after: float
    """``cp_to_win_prob`` of the two evaluations."""

    loss_cp: float = 0.0
    """``max(0, eval_before_cp - eval_after_cp)``: what the move gave away."""

    loss_wp: float = 0.0
    """``max(0, win_prob_before - win_prob_after)``: the label input."""

    best_move: str | None = None
    """UCI of the engine's first choice in the position before the move."""

    best_move_san: str | None = None
    best_move_cp: float = 0.0
    best_move_wp: float = 0.5
    """Evaluation of the engine's best move, for reference."""

    rank: int | None = None
    """1-based MultiPV rank of the played move, or ``None`` if it was not in the set."""

    n_lines: int = 1
    """How many PV lines the MultiPV search returned (fewer than requested is normal
    when the engine stops early)."""

    played_in_multipv: bool = False
    """Whether the played move was among the searched lines (then no extra search of
    the resulting position was needed)."""

    # -- criticality, merged from analysis/criticality.py --------------------------------
    is_only_move: bool = False
    gap_to_second_wp: float = 0.0
    sharpness: float = 0.0
    is_forcing: bool = False
    is_critical: bool = False


class ThemeHitModel(BaseModel):
    """Serialised form of ``themes.base.ThemeHit``."""

    model_config = ConfigDict(validate_assignment=True)

    theme: str
    """A name from :data:`moveexp.config.THEME_VOCAB`."""

    squares: list[str] = Field(default_factory=list)
    """Algebraic squares involved, most relevant first."""

    pieces: list[str] = Field(default_factory=list)
    """Human-readable pieces, e.g. ``"N@f5"``."""

    confidence: float = 1.0
    """1.0 for an exact rule match; lower when a detector had to guess."""

    evidence: str = ""
    """One-line justification, shown verbatim in LLM prompts and in label audits."""


class IntentTagModel(BaseModel):
    """Serialised form of ``themes.intent.IntentTag``."""

    model_config = ConfigDict(validate_assignment=True)

    tag: str
    """A name from :data:`moveexp.config.INTENT_VOCAB`."""

    evidence: str = ""
    moves: list[str] = Field(default_factory=list)
    """SAN/uci moves that justify the tag (e.g. the threatening move found by a probe)."""

    confidence: float = 1.0
    """1.0 for an exact rule match; lower when a detector had to guess."""


class PositionalDelta(BaseModel):
    """Change in the positional feature groups, from the mover's point of view.

    Each field is ``after - before`` for the side that played the move; a positive
    number means "the move improved that aspect". See ``features.py``.
    """

    model_config = ConfigDict(validate_assignment=True, extra="allow")

    material: float = 0.0
    mobility: float = 0.0
    king_safety: float = 0.0
    pawn_structure: float = 0.0
    space: float = 0.0
    activity: float = 0.0


class AnalysisMeta(BaseModel):
    """Provenance of a report: which engine settings produced it."""

    model_config = ConfigDict(validate_assignment=True)

    engine_path: str | None = None
    engine_id: str | None = None
    limit_signature: str = ""
    """Cache/label signature of the analysis budget, e.g. ``"d16"`` or ``"n300000"``."""

    depth: int = 0
    nodes: int = 0
    multipv: int = 1
    tier: int = 1
    """1 = cheap bulk pass, 2 = re-analysis of flagged positions."""

    source: str = "engine"
    """``"engine"`` | ``"eval_db"`` | ``"puzzle"``."""

    label_source: str = "rule"
    """``"rule"`` (detectors), ``"puzzle_tag"`` (independent ground truth) or
    ``"engine"`` (engine-derived fields)."""

    puzzle_tags: list[str] = Field(default_factory=list)
    """Ground-truth theme tags, when the position came from the puzzle database."""

    cache_hit: bool = False
    dataset_version: str = DATASET_VERSION


class EngineProvenance(BaseModel):
    """What engine (and settings) produced the numbers in a report.

    Labels are only comparable when they came from the same engine version and search
    settings, so every report records this. Filled from the engine's own handshake
    (``engine.id``), never from config.
    """

    model_config = ConfigDict(validate_assignment=True)

    engine_name: str = ""
    """The engine's ``id name`` string, e.g. ``"Stockfish 19"``."""

    engine_author: str = ""
    """The engine's ``id author`` string."""

    limit_type: str = ""
    """``"depth"`` | ``"nodes"`` | ``"movetime"`` — which budget the search used."""

    limit_value: float | None = None
    """The numeric budget value (depth plies, node count, or seconds)."""

    multipv: int = 1
    threads: int = 1
    hash_mb: int = 0
    moveexp_version: str = ""
    """The ``moveexp`` package version that produced the report."""


class MoveReport(BaseModel):
    """Everything the symbolic layer knows about one played move."""

    model_config = ConfigDict(validate_assignment=True)

    ply: int
    """Half-move index from the start of the game."""

    fen_before: str
    """Full FEN of the position before the move."""

    move_uci: str
    move_san: str

    quality: QualityInfo
    themes: list[ThemeHitModel] = Field(default_factory=list)
    positional_delta: PositionalDelta = Field(default_factory=PositionalDelta)
    intent: list[IntentTagModel] = Field(default_factory=list)
    pv: list[str] = Field(default_factory=list)
    """UCI moves of the engine's preferred continuation after the played move."""

    fen_after: str | None = None
    meta: AnalysisMeta = Field(default_factory=AnalysisMeta)
    provenance: EngineProvenance = Field(default_factory=EngineProvenance)

    # -- convenience accessors ---------------------------------------------------------
    @property
    def theme_names(self) -> list[str]:
        """De-duplicated theme names in detection order."""
        seen: dict[str, None] = {}
        for hit in self.themes:
            seen.setdefault(hit.theme, None)
        return list(seen)

    @property
    def intent_tags(self) -> list[str]:
        """De-duplicated intent tags in detection order."""
        seen: dict[str, None] = {}
        for tag in self.intent:
            seen.setdefault(tag.tag, None)
        return list(seen)

    # -- parquet helpers ---------------------------------------------------------------
    def to_flat_row(self) -> dict[str, Any]:
        """Flatten into a single Parquet-friendly row.

        Nested structures become JSON strings (they are only needed for audits) and the
        multi-label targets become fixed-order 0/1 vectors so that the dataset can be
        streamed without re-parsing text.
        """
        theme_vec = theme_multi_hot(self.theme_names)
        intent_vec = intent_multi_hot(self.intent_tags)
        return {
            "dataset_version": self.meta.dataset_version,
            "ply": self.ply,
            "fen_before": self.fen_before,
            "fen_after": self.fen_after,
            "move_uci": self.move_uci,
            "move_san": self.move_san,
            # quality
            "label": self.quality.label,
            "eval_before_cp": float(self.quality.eval_before_cp),
            "eval_after_cp": float(self.quality.eval_after_cp),
            "win_prob_before": float(self.quality.win_prob_before),
            "win_prob_after": float(self.quality.win_prob_after),
            "loss_cp": float(self.quality.loss_cp),
            "loss_wp": float(self.quality.loss_wp),
            "best_move": self.quality.best_move,
            "best_move_san": self.quality.best_move_san,
            "best_move_cp": float(self.quality.best_move_cp),
            "best_move_wp": float(self.quality.best_move_wp),
            "rank": self.quality.rank,
            "n_lines": int(self.quality.n_lines),
            "played_in_multipv": bool(self.quality.played_in_multipv),
            # criticality
            "is_only_move": bool(self.quality.is_only_move),
            "gap_to_second_wp": float(self.quality.gap_to_second_wp),
            "sharpness": float(self.quality.sharpness),
            "is_forcing": bool(self.quality.is_forcing),
            "is_critical": bool(self.quality.is_critical),
            # themes + intent
            "themes": json.dumps([hit.model_dump() for hit in self.themes]),
            "intents": json.dumps([tag.model_dump() for tag in self.intent]),
            "theme_vector": theme_vec,
            "intent_vector": intent_vec,
            "theme_mask": int(any(theme_vec)),
            "intent_mask": int(any(intent_vec)),
            # positional delta
            **{f"delta_{k}": float(v) for k, v in self.positional_delta.model_dump().items()},
            # engine metadata
            "pv": " ".join(self.pv),
            "pv_san": " ".join(_pv_to_san(self.fen_after, self.pv)),
            "engine_depth": int(self.meta.depth),
            "engine_nodes": int(self.meta.nodes),
            "multipv": int(self.meta.multipv),
            "tier": int(self.meta.tier),
            "limit_signature": self.meta.limit_signature,
            "source": self.meta.source,
            "label_source": self.meta.label_source,
            "puzzle_tags": " ".join(self.meta.puzzle_tags),
            "cache_hit": bool(self.meta.cache_hit),
            # engine provenance
            "prov_engine_name": self.provenance.engine_name,
            "prov_engine_author": self.provenance.engine_author,
            "prov_limit_type": self.provenance.limit_type,
            "prov_limit_value": self.provenance.limit_value,
            "prov_multipv": int(self.provenance.multipv),
            "prov_threads": int(self.provenance.threads),
            "prov_hash_mb": int(self.provenance.hash_mb),
            "prov_moveexp_version": self.provenance.moveexp_version,
        }

    @classmethod
    def from_flat_row(cls, row: Mapping[str, Any]) -> MoveReport:
        """Inverse of :meth:`to_flat_row` (used by the audit and stats scripts)."""
        delta_keys = ("material", "mobility", "king_safety", "pawn_structure", "space", "activity")
        delta = PositionalDelta(**{k: row.get(f"delta_{k}", 0.0) or 0.0 for k in delta_keys})
        for key, value in row.items():
            if key.startswith("delta_") and key[len("delta_") :] not in delta_keys:
                setattr(delta, key[len("delta_") :], value or 0.0)
        quality = QualityInfo(
            label=str(row["label"]),
            eval_before_cp=float(row["eval_before_cp"]),
            eval_after_cp=float(row["eval_after_cp"]),
            win_prob_before=float(row["win_prob_before"]),
            win_prob_after=float(row["win_prob_after"]),
            loss_cp=float(row.get("loss_cp", 0.0) or 0.0),
            loss_wp=float(row.get("loss_wp", 0.0) or 0.0),
            best_move=row.get("best_move"),
            best_move_san=row.get("best_move_san"),
            best_move_cp=float(row.get("best_move_cp", 0.0) or 0.0),
            best_move_wp=float(row.get("best_move_wp", 0.5) or 0.5),
            rank=None if row.get("rank") is None else int(row["rank"]),
            n_lines=int(row.get("n_lines", 1) or 1),
            played_in_multipv=bool(row.get("played_in_multipv", False)),
            is_only_move=bool(row.get("is_only_move", False)),
            gap_to_second_wp=float(row.get("gap_to_second_wp", 0.0) or 0.0),
            sharpness=float(row.get("sharpness", 0.0) or 0.0),
            is_forcing=bool(row.get("is_forcing", False)),
            is_critical=bool(row.get("is_critical", False)),
        )
        pv_str = row.get("pv") or ""
        return cls(
            ply=int(row["ply"]),
            fen_before=str(row["fen_before"]),
            move_uci=str(row["move_uci"]),
            move_san=str(row.get("move_san", "")),
            quality=quality,
            themes=[ThemeHitModel(**h) for h in json.loads(row.get("themes") or "[]")],
            positional_delta=delta,
            intent=[IntentTagModel(**t) for t in json.loads(row.get("intents") or "[]")],
            pv=[m for m in str(pv_str).split(" ") if m],
            fen_after=row.get("fen_after"),
            meta=AnalysisMeta(
                engine_path=row.get("engine_path"),
                limit_signature=str(row.get("limit_signature", "")),
                depth=int(row.get("engine_depth", 0) or 0),
                nodes=int(row.get("engine_nodes", 0) or 0),
                multipv=int(row.get("multipv", 1) or 1),
                tier=int(row.get("tier", 1) or 1),
                source=str(row.get("source", "engine")),
                label_source=str(row.get("label_source", "rule")),
                puzzle_tags=[t for t in str(row.get("puzzle_tags") or "").split(" ") if t],
                cache_hit=bool(row.get("cache_hit", False)),
                dataset_version=str(row.get("dataset_version", DATASET_VERSION)),
            ),
            provenance=EngineProvenance(
                engine_name=str(row.get("prov_engine_name", "") or ""),
                engine_author=str(row.get("prov_engine_author", "") or ""),
                limit_type=str(row.get("prov_limit_type", "") or ""),
                limit_value=row.get("prov_limit_value"),
                multipv=int(row.get("prov_multipv", 1) or 1),
                threads=int(row.get("prov_threads", 1) or 1),
                hash_mb=int(row.get("prov_hash_mb", 0) or 0),
                moveexp_version=str(row.get("prov_moveexp_version", "") or ""),
            ),
        )


class GameReport(BaseModel):
    """A sequence of :class:`MoveReport` plus the metadata of the game it came from."""

    model_config = ConfigDict(validate_assignment=True)

    game_id: str
    source: str = "game"
    """``"game"`` | ``"puzzle"``."""

    fen_start: str | None = None
    split: str = ""
    """``"train"`` | ``"val"`` | ``"test"``, assigned at sampling time from the *game* id."""

    players: dict[str, str] = Field(default_factory=dict)
    result: str | None = None
    moves: list[MoveReport] = Field(default_factory=list)
    meta: AnalysisMeta = Field(default_factory=AnalysisMeta)
    provenance: EngineProvenance = Field(default_factory=EngineProvenance)

    def to_flat_rows(self) -> list[dict[str, Any]]:
        """Flatten the game into labelled rows, each carrying ``game_id`` and ``split``."""
        return [
            {"game_id": self.game_id, "split": self.split, **r.to_flat_row()} for r in self.moves
        ]

    def to_parquet(self, path: str, *, append: bool = False) -> int:
        """Write every move as one row. Returns the number of rows written.

        ``pandas``/``pyarrow`` are imported lazily so that importing ``moveexp.schema``
        stays cheap and does not require the data stack.
        """
        import pandas as pd

        rows = self.to_flat_rows()
        frame = pd.DataFrame(rows)
        frame.to_parquet(path, engine="pyarrow", index=False, append=append)
        return len(frame)


# --------------------------------------------------------------------------------------
# Multi-hot label vectors
# --------------------------------------------------------------------------------------


def theme_multi_hot(themes: Iterable[str], vocab: Sequence[str] = THEME_VOCAB) -> list[int]:
    """Expand theme names into a 0/1 vector in ``vocab`` order.

    Unknown names are ignored *and reported*: they usually mean a detector emitted a
    theme that is missing from :data:`moveexp.config.THEME_VOCAB`, which would silently
    drop that label from the training target.
    """
    return _multi_hot(themes, vocab, kind="theme")


def intent_multi_hot(tags: Iterable[str], vocab: Sequence[str] = INTENT_VOCAB) -> list[int]:
    """Expand intent tags into a 0/1 vector in ``vocab`` order."""
    return _multi_hot(tags, vocab, kind="intent")


def _multi_hot(names: Iterable[str], vocab: Sequence[str], *, kind: str) -> list[int]:
    wanted = set(names)
    vector = [1 if name in wanted else 0 for name in vocab]
    unknown = sorted(n for n in wanted if n not in set(vocab))
    if unknown:
        raise KeyError(
            f"unknown {kind} label(s) {unknown}; add them to moveexp.config."
            f"{kind.upper()}_VOCAB (append only) before labelling data"
        )
    return vector


def labels_from_multi_hot(vector: Sequence[int], vocab: Sequence[str]) -> tuple[str, ...]:
    """Inverse of :func:`theme_multi_hot` / :func:`intent_multi_hot`."""
    if len(vector) != len(vocab):
        raise ValueError(f"vector length {len(vector)} does not match vocab length {len(vocab)}")
    return tuple(name for name, flag in zip(vocab, vector, strict=True) if flag)


def quality_to_index(label: str) -> int:
    """Class index of a quality label for the neural model's softmax head."""
    try:
        return QUALITY_LABELS.index(label)
    except ValueError as exc:  # pragma: no cover - defensive
        raise KeyError(
            f"unknown quality label {label!r}; expected one of {QUALITY_LABELS}"
        ) from exc


#: Column order of the multi-hot targets, handy for Parquet schemas and test asserts.
THEME_VECTOR_LENGTH: Final[int] = len(THEME_VOCAB)
INTENT_VECTOR_LENGTH: Final[int] = len(INTENT_VOCAB)


def _pv_to_san(fen: str | None, pv: Sequence[str]) -> list[str]:
    """Best-effort PV-to-SAN conversion (empty list if the position is unusable)."""
    if not fen or not pv:
        return []
    try:
        board = chess.Board(fen)
    except ValueError:
        return []
    sans: list[str] = []
    for uci in pv:
        try:
            move = chess.Move.from_uci(uci)
        except ValueError:
            break
        if move not in board.legal_moves:
            break
        sans.append(board.san(move))
        board.push(move)
    return sans
