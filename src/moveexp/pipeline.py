"""The full report pipeline: engine + quality + criticality + themes + delta + intent.

Milestone 1's ``cli.analyse_single_move`` built a Stage-1-only report (quality and
criticality). This module is the real thing: it layers the theme detectors, the positional
delta and the intent tags on top, and is what ``analyze-move`` / ``analyze-pgn`` / ``batch``
all call.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import chess
import chess.pgn

from . import __version__
from .analysis.criticality import assess_criticality
from .analysis.features import positional_delta
from .analysis.move_quality import MoveQuality, assess_move, classify_special
from .analysis.see import is_sacrifice
from .analysis.themes import register_all
from .analysis.themes.base import DetectionContext, run_all
from .analysis.themes.intent import IntentContext, detect_intents, threat_probe
from .config import (
    DEFAULT_ENGINE_PATH,
    DEFAULT_HASH_MB,
    DEFAULT_MULTIPV,
    DEFAULT_THREADS,
    NULL_MOVE_PROBE_DEPTH,
)
from .engine.cache import AnalysisCache
from .engine.client import AnalysisLimit, StockfishClient
from .schema import (
    AnalysisMeta,
    EngineProvenance,
    GameReport,
    MoveReport,
    PositionalDelta,
    QualityInfo,
)

__all__ = ["analyse_game", "analyse_move"]


class _NullCache:
    """Stand-in for :class:`~moveexp.engine.cache.AnalysisCache` when caching is disabled."""

    def __enter__(self) -> None:
        return None

    def __exit__(self, *exc: object) -> None:
        return None


def _pv_uci(lines_before, move: chess.Move, lines_after) -> list[str]:
    """Engine's preferred continuation after the played move, as UCI."""
    if lines_after:
        return list(lines_after[0].pv)
    for line in lines_before:
        if line.move == move.uci():
            return list(line.pv)
    return []


def _provenance(
    engine_name: str | None,
    engine_author: str | None,
    limit: AnalysisLimit,
    multipv: int,
    threads: int,
    hash_mb: int,
) -> EngineProvenance:
    """Build the :class:`~moveexp.schema.EngineProvenance` for one analysis run."""
    if limit.depth is not None:
        limit_type, limit_value = "depth", float(limit.depth)
    elif limit.nodes is not None:
        limit_type, limit_value = "nodes", float(limit.nodes)
    else:
        limit_type = "movetime"
        limit_value = float(limit.movetime) if limit.movetime is not None else None
    return EngineProvenance(
        engine_name=engine_name or "",
        engine_author=engine_author or "",
        limit_type=limit_type,
        limit_value=limit_value,
        multipv=multipv,
        threads=threads,
        hash_mb=hash_mb,
        moveexp_version=__version__,
    )


def _resolve_special(
    quality: MoveQuality,
    board_before: chess.Board,
    move: chess.Move,
    lines_before,
) -> MoveQuality:
    """Apply the optional ``great`` / ``brilliant`` label, with engine-confirmed sacrifice."""
    sacrifice, _ = is_sacrifice(board_before, move)
    sacrifice_confirmed = sacrifice and quality.win_prob_after >= quality.win_prob_before
    special = classify_special(
        quality, board_before, move, lines_before, sacrifice_confirmed=sacrifice_confirmed
    )
    return quality.with_label(special) if special is not None else quality


def _analyse_with_client(
    client: StockfishClient,
    board_before: chess.Board,
    move: chess.Move,
    limit: AnalysisLimit,
    multipv: int,
    run_intent: bool,
    null_move_probes: bool,
):
    """Run the engine + quality half of the pipeline on an already-open client."""
    hits_before = client.stats.cache_hits
    lines_before, lines_after = client.analyse_pair(board_before, move, limit, multipv=multipv)
    cache_hit = client.stats.cache_hits > hits_before
    engine_id = client.engine_id
    engine_author = client.engine_author
    quality = _resolve_special(
        assess_move(board_before, move, lines_before, lines_after),
        board_before,
        move,
        lines_before,
    )
    probe_tags = None
    if null_move_probes:
        probe_tags = threat_probe(
            client, board_before, move, AnalysisLimit.by_depth(NULL_MOVE_PROBE_DEPTH)
        )
    return lines_before, lines_after, cache_hit, engine_id, engine_author, quality, probe_tags


def analyse_move(
    board_before: chess.Board,
    move: chess.Move,
    *,
    client: StockfishClient | None = None,
    engine_path: str = DEFAULT_ENGINE_PATH,
    threads: int = DEFAULT_THREADS,
    hash_mb: int = DEFAULT_HASH_MB,
    limit: AnalysisLimit | None = None,
    multipv: int = DEFAULT_MULTIPV,
    cache_db: Path | None = None,
    use_cache: bool = True,
    run_intent: bool = True,
    null_move_probes: bool = False,
    ply: int = 0,
) -> MoveReport:
    """Analyse one move and return a complete :class:`MoveReport`.

    :param board_before: the position before ``move`` (never mutated).
    :param move: the played move, legal in ``board_before``.
    :param client: an already-open :class:`~moveexp.engine.client.StockfishClient` to reuse;
        when omitted, one is opened (and closed) for this call.
    :param limit: search budget (defaults to the configured depth).
    :param null_move_probes: run the optional engine threat probes (extra cost; see README).
    :param ply: half-move index from the start of the game.
    """
    register_all()
    limit = limit or AnalysisLimit.from_any()

    if client is not None:
        lines_before, lines_after, cache_hit, engine_id, engine_author, quality, probe_tags = (
            _analyse_with_client(
                client, board_before, move, limit, multipv, run_intent, null_move_probes
            )
        )
    else:
        cache_ctx = AnalysisCache(cache_db) if use_cache and cache_db is not None else _NullCache()
        with (
            cache_ctx as cache,
            StockfishClient(
                engine_path, threads=threads, hash_mb=hash_mb, multipv=multipv, cache=cache
            ) as owned,
        ):
            lines_before, lines_after, cache_hit, engine_id, engine_author, quality, probe_tags = (
                _analyse_with_client(
                    owned, board_before, move, limit, multipv, run_intent, null_move_probes
                )
            )

    provenance = _provenance(engine_id, engine_author, limit, multipv, threads, hash_mb)

    board_after = board_before.copy(stack=False)
    board_after.push(move)

    criticality = assess_criticality(
        board_before,
        move,
        board_after,
        lines_before,
        win_prob_before=quality.win_prob_before,
        win_prob_after=quality.win_prob_after,
    )

    detection = DetectionContext.from_move(board_before, move)
    themes = run_all(detection)
    delta = positional_delta(board_before, move)

    intents = []
    if run_intent:
        intents = detect_intents(IntentContext.from_detection(detection, themes))
        if probe_tags:
            intents = sorted(intents + probe_tags, key=lambda tag: tag.sort_key())

    return MoveReport(
        ply=ply,
        fen_before=board_before.fen(),
        fen_after=board_after.fen(),
        move_uci=move.uci(),
        move_san=board_before.san(move),
        quality=QualityInfo(
            label=quality.label,
            eval_before_cp=quality.eval_before_cp,
            eval_after_cp=quality.eval_after_cp,
            win_prob_before=quality.win_prob_before,
            win_prob_after=quality.win_prob_after,
            loss_cp=quality.loss_cp,
            loss_wp=quality.loss_wp,
            best_move=quality.best_move,
            best_move_san=quality.best_move_san,
            best_move_cp=quality.best_move_cp,
            best_move_wp=quality.best_move_wp,
            rank=quality.rank,
            n_lines=quality.n_lines,
            played_in_multipv=quality.played_in_multipv,
            is_only_move=criticality.is_only_move,
            gap_to_second_wp=criticality.gap_to_second_wp,
            sharpness=criticality.sharpness,
            is_forcing=criticality.is_forcing,
            is_critical=criticality.is_critical,
        ),
        themes=[hit.to_model() for hit in themes],
        positional_delta=delta if isinstance(delta, PositionalDelta) else PositionalDelta(**delta),
        intent=[tag.to_model() for tag in intents],
        pv=_pv_uci(lines_before, move, lines_after),
        meta=AnalysisMeta(
            engine_path=engine_path,
            engine_id=engine_id,
            cache_hit=cache_hit,
            limit_signature=limit.signature,
            depth=max((line.depth for line in lines_before), default=0),
            nodes=max((line.nodes for line in lines_before), default=0),
            multipv=multipv,
            tier=1,
            source="engine",
            label_source="engine",
        ),
        provenance=provenance,
    )


def _game_id(game: chess.pgn.Game) -> str:
    """Deterministic id for a game: a hash of its move list (falls back to ``Site``)."""
    site = game.headers.get("Site", "")
    if site:
        return site
    moves = " ".join(move.uci() for move in game.mainline_moves())
    return hashlib.sha1(moves.encode("utf-8")).hexdigest()[:16]


def analyse_game(
    game: chess.pgn.Game,
    *,
    client: StockfishClient | None = None,
    engine_path: str = DEFAULT_ENGINE_PATH,
    threads: int = DEFAULT_THREADS,
    hash_mb: int = DEFAULT_HASH_MB,
    limit: AnalysisLimit | None = None,
    multipv: int = DEFAULT_MULTIPV,
    cache_db: Path | None = None,
    use_cache: bool = True,
    run_intent: bool = True,
    null_move_probes: bool = False,
    max_plies: int = 0,
) -> GameReport:
    """Analyse every move of one PGN game and return a :class:`GameReport`.

    One engine process is reused for the whole game. ``client`` may be an already-open
    engine, which is then reused and left open.

    :param max_plies: stop after this many plies (``0`` = whole game); handy for smoke tests.
    """
    board = game.board()
    limit = limit or AnalysisLimit.from_any()

    def _run(c: StockfishClient) -> list[MoveReport]:
        reports: list[MoveReport] = []
        for ply, move in enumerate(game.mainline_moves()):
            if max_plies and ply >= max_plies:
                break
            reports.append(
                analyse_move(
                    board,
                    move,
                    client=c,
                    engine_path=engine_path,
                    limit=limit,
                    multipv=multipv,
                    run_intent=run_intent,
                    null_move_probes=null_move_probes,
                    ply=ply,
                )
            )
            board.push(move)
        return reports

    if client is not None:
        reports = _run(client)
        provenance = _provenance(
            client.engine_id, client.engine_author, limit, multipv, threads, hash_mb
        )
    else:
        cache_ctx = AnalysisCache(cache_db) if use_cache and cache_db is not None else _NullCache()
        with (
            cache_ctx as cache,
            StockfishClient(
                engine_path, threads=threads, hash_mb=hash_mb, multipv=multipv, cache=cache
            ) as owned,
        ):
            reports = _run(owned)
            provenance = _provenance(
                owned.engine_id, owned.engine_author, limit, multipv, threads, hash_mb
            )

    return GameReport(
        game_id=_game_id(game),
        source="game",
        players={"white": game.headers.get("White", ""), "black": game.headers.get("Black", "")},
        result=game.headers.get("Result"),
        moves=reports,
        meta=AnalysisMeta(
            engine_path=engine_path,
            engine_id=None,
            limit_signature=limit.signature,
            multipv=multipv,
            tier=1,
            source="engine",
            label_source="engine",
        ),
        provenance=provenance,
    )
