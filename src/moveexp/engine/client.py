"""Stockfish lifecycle, search budgets and result parsing.

One :class:`StockfishClient` owns one UCI engine process for its whole lifetime. That
matters for throughput: starting Stockfish costs ~50 ms and its hash table has to be
re-warmed, so bulk labelling keeps a single client per worker process and reuses it for
every position.

Two analysis budgets are supported, exposed through one :class:`AnalysisLimit`:

* **depth** -- reproducible in the sense that the result depends only on the position and
  the depth, but the wall-clock cost varies by an order of magnitude across positions.
  Used for careful analysis and for the deep (tier 2) labelling pass.
* **nodes** -- constant cost per position, which is what you want for throughput
  budgeting, at the price of very uneven search depths.

MultiPV width is a per-call option because tier-1 (MultiPV 3) and probe (MultiPV 1)
analyses are interleaved.

Crash handling: a crashed or hung engine is restarted once and the query retried. If the
retry also fails, :class:`EngineCrashedError` is raised so a bulk job can log the
position and move on rather than silently producing wrong labels.
"""

from __future__ import annotations

import contextlib
import logging
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import chess
import chess.engine

from ..config import (
    DEFAULT_DEPTH,
    DEFAULT_ENGINE_PATH,
    DEFAULT_HASH_MB,
    DEFAULT_MULTIPV,
    DEFAULT_NODES,
    DEFAULT_THREADS,
    ENGINE_QUERY_TIMEOUT_S,
    ENGINE_RESTART_ATTEMPTS,
    ENGINE_START_TIMEOUT_S,
)
from ..schema import LineInfo
from .cache import AnalysisCache, make_cache_key

__all__ = [
    "AnalysisLimit",
    "EngineError",
    "EngineCrashedError",
    "EngineNotRunningError",
    "StockfishClient",
]

LOGGER = logging.getLogger(__name__)


class EngineError(RuntimeError):
    """Base class for every engine-layer failure."""


class EngineNotRunningError(EngineError):
    """Raised when the engine is used outside its context manager or after a failed start."""


class EngineCrashedError(EngineError):
    """Raised when the engine failed twice on the same query (crash, hang or death)."""


@dataclass(frozen=True)
class AnalysisLimit:
    """A search budget: depth, nodes, or a time limit (exactly one of those three).

    ``max_seconds`` is an optional *safety net*: python-chess cannot put a timeout on
    ``analyse()``, so the client also passes it to the engine as a wall-clock limit. It
    never triggers in normal operation (a depth-16 search is milliseconds) but it stops a
    pathological position from hanging a bulk-labelling run. The client fills it in
    automatically from :data:`moveexp.config.ENGINE_QUERY_TIMEOUT_S`, and it is excluded
    from :attr:`signature` so that it does not fragment the cache.

    ``signature`` is what ends up in cache keys and in the dataset's ``limit_signature``
    column, so it must change whenever the result would change.
    """

    depth: int | None = None
    nodes: int | None = None
    movetime: float | None = None
    max_seconds: float | None = None

    def __post_init__(self) -> None:
        given = [name for name in ("depth", "nodes", "movetime") if getattr(self, name) is not None]
        if len(given) != 1:
            raise ValueError(
                f"AnalysisLimit needs exactly one of depth/nodes/movetime, got {given or 'none'}"
            )
        if self.depth is not None and self.depth < 1:
            raise ValueError("depth must be >= 1")
        if self.nodes is not None and self.nodes < 1:
            raise ValueError("nodes must be >= 1")
        if self.movetime is not None and self.movetime <= 0:
            raise ValueError("movetime must be > 0")
        if self.max_seconds is not None and self.max_seconds <= 0:
            raise ValueError("max_seconds must be > 0")
        if self.movetime is not None and self.max_seconds is not None:
            raise ValueError("movetime is already a wall-clock budget; do not set max_seconds")

    @classmethod
    def by_depth(
        cls, depth: int = DEFAULT_DEPTH, *, max_seconds: float | None = None
    ) -> AnalysisLimit:
        """Fixed search depth (careful analysis, tier-2 labelling)."""
        return cls(depth=int(depth), max_seconds=max_seconds)

    @classmethod
    def by_nodes(cls, nodes: int = 300_000, *, max_seconds: float | None = None) -> AnalysisLimit:
        """Fixed node budget (bulk labelling)."""
        return cls(nodes=int(nodes), max_seconds=max_seconds)

    def with_max_seconds(self, seconds: float) -> AnalysisLimit:
        """Return the same budget with a wall-clock safety net attached."""
        if self.max_seconds is not None or self.movetime is not None:
            return self
        return AnalysisLimit(
            depth=self.depth, nodes=self.nodes, movetime=self.movetime, max_seconds=seconds
        )

    @property
    def signature(self) -> str:
        """Short stable tag, e.g. ``"d16"``, ``"n300000"``, ``"t1.5"``."""
        if self.depth is not None:
            return f"d{self.depth}"
        if self.nodes is not None:
            return f"n{self.nodes}"
        assert self.movetime is not None
        return f"t{self.movetime:g}"

    def to_uci_limit(self) -> chess.engine.Limit:
        """Convert to the python-chess limit object."""
        return chess.engine.Limit(
            depth=self.depth,
            nodes=self.nodes,
            time=self.movetime if self.movetime is not None else self.max_seconds,
        )

    @classmethod
    def from_any(
        cls,
        depth: int | None = None,
        nodes: int | None = None,
        movetime: float | None = None,
    ) -> AnalysisLimit:
        """Build a limit from optional overrides, falling back to the configured default."""
        if depth is not None:
            return cls.by_depth(depth)
        if nodes is not None:
            return cls.by_nodes(nodes)
        if movetime is not None:
            return cls(movetime=movetime)
        if DEFAULT_NODES is not None:
            return cls.by_nodes(DEFAULT_NODES)
        return cls.by_depth(DEFAULT_DEPTH)

    def __str__(self) -> str:
        return self.signature


@dataclass
class ClientStats:
    """Counters for one client, useful in bulk-labelling logs."""

    searches: int = 0
    cache_hits: int = 0
    crashes: int = 0
    restarts: int = 0
    total_nodes: int = 0

    def as_dict(self) -> dict[str, int]:
        """Plain dict for JSON logging."""
        return {
            "searches": self.searches,
            "cache_hits": self.cache_hits,
            "crashes": self.crashes,
            "restarts": self.restarts,
            "total_nodes": self.total_nodes,
        }


class StockfishClient:
    """Context-managed wrapper around a single UCI engine process.

    ::

        with StockfishClient(threads=1, hash_mb=256) as client:
            lines = client.analyse(board, AnalysisLimit.by_depth(16), multipv=3)

    :param path: UCI executable (e.g. ``"stockfish"`` or ``"C:/engines/stockfish.exe"``).
    :param threads: UCI ``Threads``. Keep at 1 when running one process per core.
    :param hash_mb: UCI ``Hash`` in MiB.
    :param multipv: default MultiPV width.
    :param cache: optional :class:`~moveexp.engine.cache.AnalysisCache`; when given,
        :meth:`analyse` is served from / written to the cache.
    :param use_cache: set to ``False`` to bypass the cache for exploratory calls.
    """

    def __init__(
        self,
        path: str = DEFAULT_ENGINE_PATH,
        *,
        threads: int = DEFAULT_THREADS,
        hash_mb: int = DEFAULT_HASH_MB,
        multipv: int = DEFAULT_MULTIPV,
        cache: AnalysisCache | None = None,
        use_cache: bool = True,
        engine_args: Sequence[str] | None = None,
        logger: logging.Logger | None = None,
        stats: ClientStats | None = None,
    ) -> None:
        if multipv < 1:
            raise ValueError("multipv must be >= 1")
        self.path = path
        self.threads = max(1, int(threads))
        self.hash_mb = max(1, int(hash_mb))
        self.default_multipv = int(multipv)
        self.cache = cache
        self.use_cache = bool(use_cache) and cache is not None
        self.engine_args = list(engine_args) if engine_args else []
        self.log = logger or LOGGER
        self.stats = stats or ClientStats()
        self._engine: chess.engine.SimpleEngine | None = None
        self._engine_id: str | None = None
        self._engine_author: str | None = None

    # -- lifecycle ---------------------------------------------------------------------
    def __enter__(self) -> StockfishClient:
        self.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    @property
    def is_running(self) -> bool:
        """Whether the engine process is currently usable."""
        return self._engine is not None

    @property
    def engine_id(self) -> str | None:
        """The engine's ``id name ...`` string, or ``None`` before the first start."""
        return self._engine_id

    @property
    def engine_author(self) -> str | None:
        """The engine's ``id author ...`` string, or ``None`` before the first start."""
        return self._engine_author

    def start(self) -> None:
        """Start the engine process and apply persistent options."""
        if self._engine is not None:
            return
        try:
            self._engine = chess.engine.SimpleEngine.popen_uci(
                self.path, timeout=ENGINE_START_TIMEOUT_S
            )
            self._engine.configure({"Threads": self.threads, "Hash": self.hash_mb})
            self._engine_id = self._engine.id.get("name")
            self._engine_author = self._engine.id.get("author")
            self.log.debug("started engine %r at %r", self._engine_id, self.path)
        except (chess.engine.EngineError, OSError, FileNotFoundError) as exc:
            self._engine = None
            raise EngineNotRunningError(
                f"could not start UCI engine at {self.path!r}. Install Stockfish 16+ or pass "
                f"--engine-path / STOCKFISH_PATH. Original error: {exc}"
            ) from exc

    def close(self) -> None:
        """Quit the engine process if it is running."""
        engine, self._engine = self._engine, None
        if engine is None:
            return
        try:
            engine.quit()
        except (chess.engine.EngineError, OSError) as exc:  # pragma: no cover
            self.log.warning("engine did not quit cleanly: %s", exc)
            with contextlib.suppress(Exception):  # pragma: no cover - best effort
                engine.close()

    def restart(self) -> None:
        """Force-restart the engine (used after a crash)."""
        self.close()
        self.stats.restarts += 1
        self.start()

    @staticmethod
    def _ensure_searchable(board: chess.Board) -> None:
        """Reject positions that Stockfish must not be asked about.

        Engines react badly to illegal input: Stockfish 18 segfaults on an impossible
        position where a king is en prise, while 19 prints ``CRITICAL ERROR`` and stops
        reading commands. Checking here turns a crash (and an expensive restart) into a
        clear :class:`EngineError`. ``Board.status()`` is a linear scan of the pieces, not
        a retrograde analysis, so it is cheap enough to run on every position.
        """
        if board.is_game_over():
            raise EngineError(
                f"position is over ({board.outcome(claim_draw=True)}), nothing to search"
            )
        status = board.status()
        if status != chess.STATUS_VALID:
            raise EngineError(f"position is not legal for the engine: {status!r} in {board.fen()}")

    # -- analysis ----------------------------------------------------------------------
    def analyse(
        self,
        board: chess.Board,
        limit: AnalysisLimit | None = None,
        *,
        multipv: int | None = None,
        use_cache: bool | None = None,
    ) -> list[LineInfo]:
        """Search ``board`` and return the MultiPV lines, best rank first.

        Lines carry scores relative to ``board.turn`` (see :class:`~moveexp.schema.LineInfo`);
        use :func:`moveexp.engine.eval_utils.lines_to_mover_perspective` to change that.

        :param board: position to search. It is copied internally and never mutated.
        :param limit: search budget; defaults to the configured depth.
        :param multipv: number of lines; defaults to the client's default.
        :param use_cache: override the client-level cache policy for this call.
        :raises EngineNotRunningError: if the engine is not started.
        :raises EngineCrashedError: if the engine fails twice on this position.
        :raises EngineError: if the position is terminal, illegal, or yielded no score.
        """
        if self._engine is None:
            raise EngineNotRunningError("engine is not running; use `with StockfishClient(...)`")
        self._ensure_searchable(board)

        limit = limit or AnalysisLimit.from_any()
        pv_width = int(multipv if multipv is not None else self.default_multipv)
        if pv_width < 1:
            raise ValueError("multipv must be >= 1")

        cache_ok = self.use_cache if use_cache is None else bool(use_cache)
        key = (
            make_cache_key(
                board.fen(), limit.signature, pv_width, engine_version=self._engine_id or ""
            )
            if cache_ok and self.cache
            else None
        )
        if key is not None:
            cached = self.cache.get(key)  # type: ignore[union-attr]
            if cached is not None:
                self.stats.cache_hits += 1
                return cached

        lines = self._search_with_restart(board, limit, pv_width)
        if key is not None:
            self.cache.put(  # type: ignore[union-attr]
                key, lines, fen=board.fen(), limit_signature=limit.signature, multipv=pv_width
            )
        return lines

    def _search_with_restart(
        self, board: chess.Board, limit: AnalysisLimit, multipv: int
    ) -> list[LineInfo]:
        """Run :meth:`analyse`'s search, restarting the engine once if it dies."""
        last_error: BaseException | None = None
        for attempt in range(1, ENGINE_RESTART_ATTEMPTS + 1):
            try:
                lines = self._search(board, limit, multipv)
            except (chess.engine.EngineError, BrokenPipeError, OSError) as exc:
                self.stats.crashes += 1
                last_error = exc
                self.log.warning(
                    "engine failure on %s (attempt %d/%d): %s",
                    board.fen(),
                    attempt,
                    ENGINE_RESTART_ATTEMPTS,
                    exc,
                )
                if attempt < ENGINE_RESTART_ATTEMPTS:
                    self.restart()
                continue
            self.stats.searches += 1
            self.stats.total_nodes += sum(line.nodes for line in lines)
            return lines
        raise EngineCrashedError(
            f"engine failed {ENGINE_RESTART_ATTEMPTS} times on {board.fen()!r}: {last_error}"
        ) from last_error

    def _search(self, board: chess.Board, limit: AnalysisLimit, multipv: int) -> list[LineInfo]:
        """One engine round-trip and its result parsing."""
        assert self._engine is not None
        # python-chess has no per-query timeout, so the wall-clock safety net is passed as
        # part of the limit. It is not part of `signature`, hence not part of the cache key.
        limit = limit.with_max_seconds(ENGINE_QUERY_TIMEOUT_S)
        # Copy so that the engine's own bookkeeping can never touch the caller's board.
        root = board.copy(stack=False)
        # `multipv=` is a dedicated python-chess argument: it manages the UCI `MultiPV`
        # option itself and rejects it being passed through `options`.
        infos = self._engine.analyse(root, limit.to_uci_limit(), multipv=multipv)
        lines = [line for line in (self._parse_info(info, root) for info in infos) if line]
        if not lines:
            raise EngineError(f"engine returned no scored lines for {board.fen()!r}")
        lines.sort(key=lambda line: line.multipv_rank)
        return lines

    @staticmethod
    def _parse_info(info: chess.engine.InfoDict, root: chess.Board) -> LineInfo | None:
        """Convert one UCI info dict into a :class:`LineInfo` (raw, side-to-move POV).

        Lines without a score are dropped: Stockfish emits them when MultiPV is still
        filling up, and they carry no usable evaluation.
        """
        score = info.get("score")
        if score is None:
            return None
        pv = list(info.get("pv") or [])
        bound: str | None = None
        if info.get("upperbound"):
            bound = "upper"
        elif info.get("lowerbound"):
            bound = "lower"
        cp = None if score.is_mate() else score.relative.score()
        return LineInfo(
            turn=root.turn,
            move=pv[0].uci() if pv else None,
            pv=[move.uci() for move in pv],
            score_cp=None if cp is None else float(cp),
            mate=score.relative.mate(),
            depth=int(info.get("depth") or 0),
            seldepth=info.get("seldepth"),
            nodes=int(info.get("nodes") or 0),
            multipv_rank=int(info.get("multipv") or 1),
            bound=bound,
        )

    # -- convenience -------------------------------------------------------------------
    def analyse_pair(
        self,
        board_before: chess.Board,
        move: chess.Move,
        limit: AnalysisLimit | None = None,
        *,
        multipv: int | None = None,
        use_cache: bool | None = None,
    ) -> tuple[list[LineInfo], list[LineInfo] | None]:
        """Analyse the position before ``move`` and, if needed, after it.

        The second search is skipped when the played move is already among the MultiPV
        lines of the first search, which is the common case and halves the engine cost of
        labelling.

        :returns: ``(lines_before, lines_after)`` where ``lines_after`` is ``None`` when it
            was unnecessary. Both are relative to ``board_before.turn`` once passed through
            :func:`moveexp.engine.eval_utils.lines_to_mover_perspective`.
        """
        lines_before = self.analyse(board_before, limit, multipv=multipv, use_cache=use_cache)
        if any(line.move == move.uci() for line in lines_before):
            return lines_before, None
        board_after = board_before.copy(stack=False)
        board_after.push(move)
        lines_after = self.analyse(board_after, limit, multipv=1, use_cache=use_cache)
        return lines_before, lines_after

    def snapshot(self) -> dict[str, Any]:
        """Small dict of engine + client state, for logs and for ``AnalysisMeta``."""
        return {
            "engine_path": self.path,
            "engine_id": self._engine_id,
            "threads": self.threads,
            "hash_mb": self.hash_mb,
            **self.stats.as_dict(),
        }
