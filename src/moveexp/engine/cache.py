"""SQLite-backed cache for engine results.

Why a cache at all: bulk labelling searches hundreds of thousands of positions, and
transpositions are common (opening book lines repeat, and the "position after the move"
of one move is frequently also the "position before" of the next one, once the same move
order appears again in another game). Caching turns a repeat search into a SQLite lookup
and is also what makes the dataset reproducible: re-running a labelling job with the same
limit signature reuses the same numbers.

Concurrency: WAL journalling lets several worker *processes* read and write the same file
concurrently without a lock around the whole database. Counters are flushed in batches by
the owning process so that the hot path does not issue an UPDATE per cache hit.

Key: ``(normalised FEN, limit signature, MultiPV)``. The halfmove clock is deliberately
excluded (see :func:`moveexp.schema.normalise_fen`).
"""

from __future__ import annotations

import json
import os
import sqlite3
import time
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from ..config import CACHE_BUSY_TIMEOUT_S, DEFAULT_CACHE_DB
from ..schema import LineInfo, normalise_fen

__all__ = ["AnalysisCache", "CacheStats", "make_cache_key"]

_SCHEMA = """
CREATE TABLE IF NOT EXISTS analyses (
    key         TEXT PRIMARY KEY,
    payload     TEXT NOT NULL,
    fen         TEXT NOT NULL,
    limit_sig   TEXT NOT NULL,
    multipv     INTEGER NOT NULL,
    depth       INTEGER NOT NULL DEFAULT 0,
    nodes       INTEGER NOT NULL DEFAULT 0,
    created_at  REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_analyses_fen ON analyses (fen);
CREATE INDEX IF NOT EXISTS idx_analyses_created ON analyses (created_at);
CREATE TABLE IF NOT EXISTS counters (
    name  TEXT PRIMARY KEY,
    value INTEGER NOT NULL
);
"""

_COUNTERS = ("hits", "misses", "writes")


@dataclass(frozen=True)
class CacheStats:
    """Cache counters. ``hits`` / ``misses`` / ``writes`` are global across processes."""

    hits: int
    misses: int
    writes: int
    entries: int
    size_bytes: int

    @property
    def hit_rate(self) -> float:
        """Fraction of lookups served from the cache (``0.0`` when nothing was looked up)."""
        total = self.hits + self.misses
        return self.hits / total if total else 0.0

    def __str__(self) -> str:
        return (
            f"hits={self.hits} misses={self.misses} "
            f"hit_rate={self.hit_rate:.1%} entries={self.entries} "
            f"size={self.size_bytes / 2**20:.1f} MiB"
        )


def make_cache_key(
    fen: str, limit_signature: str, multipv: int, *, engine_version: str = ""
) -> str:
    """Build the cache key for one analysis.

    The engine version is part of the key so that results produced by different Stockfish
    builds (which may search differently) can never collide. Callers that do not know the
    version may omit it, but the client always passes the engine's reported name.

    :param fen: any FEN; only its normalised form is used.
    :param limit_signature: e.g. ``"d16"`` or ``"n300000"``. Must include everything that
        can change the result, including MultiPV-relevant engine options.
    :param engine_version: the engine's ``id name`` string (e.g. ``"Stockfish 19"``).
    """
    return f"{normalise_fen(fen)}|{engine_version}|{limit_signature}|{int(multipv)}"


class AnalysisCache:
    """Process-local handle on the shared SQLite analysis cache.

    Usage::

        with AnalysisCache(path) as cache:
            client = StockfishClient(cache=cache)

    One instance per process. Not thread-safe by design (SQLite connections are cheap,
    so give each thread its own) and safe to share between processes via the file.
    """

    def __init__(
        self,
        path: str | os.PathLike[str] | None = None,
        *,
        busy_timeout_s: float = CACHE_BUSY_TIMEOUT_S,
        read_only: bool = False,
    ) -> None:
        self.path = Path(path) if path is not None else DEFAULT_CACHE_DB
        self.read_only = read_only
        if not read_only:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(
            str(self.path),
            timeout=busy_timeout_s,
            isolation_level=None,  # autocommit; explicit transactions where needed
        )
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(f"PRAGMA busy_timeout = {int(busy_timeout_s * 1000)}")
        if not read_only:
            self._conn.execute("PRAGMA journal_mode = WAL")
            self._conn.execute("PRAGMA synchronous = NORMAL")
            self._conn.executescript(_SCHEMA)
        self._local = dict.fromkeys(_COUNTERS, 0)
        self._dirty = False

    # -- context management ------------------------------------------------------------
    def __enter__(self) -> AnalysisCache:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        """Flush counters and close the connection."""
        try:
            self.flush_counters()
        finally:
            self._conn.close()

    # -- core operations ---------------------------------------------------------------
    def get(self, key: str) -> list[LineInfo] | None:
        """Return cached lines for ``key``, or ``None`` on a miss.

        A cached payload that cannot be parsed (e.g. written by an older schema) is
        treated as a miss and deleted, so one bad row cannot poison a labelling run.
        """
        row = self._conn.execute("SELECT payload FROM analyses WHERE key = ?", (key,)).fetchone()
        if row is None:
            self._local["misses"] += 1
            self._dirty = True
            return None
        try:
            lines = [LineInfo(**item) for item in json.loads(row["payload"])]
        except (ValueError, TypeError):
            self._conn.execute("DELETE FROM analyses WHERE key = ?", (key,))
            self._local["misses"] += 1
            self._dirty = True
            return None
        self._local["hits"] += 1
        self._dirty = True
        return lines

    def put(
        self,
        key: str,
        lines: Sequence[LineInfo],
        *,
        fen: str | None = None,
        limit_signature: str = "",
        multipv: int = 1,
    ) -> None:
        """Store ``lines`` under ``key``, replacing any previous entry."""
        if not lines:
            return
        payload = json.dumps([line.model_dump(mode="json") for line in lines])
        first = lines[0]
        self._conn.execute(
            "INSERT OR REPLACE INTO analyses"
            " (key, payload, fen, limit_sig, multipv, depth, nodes, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                key,
                payload,
                normalise_fen(fen) if fen is not None else key.split("|")[0],
                limit_signature or key.split("|")[1],
                int(multipv),
                int(first.depth),
                int(first.nodes),
                time.time(),
            ),
        )
        self._local["writes"] += 1
        self._dirty = True

    def flush_counters(self, *, force: bool = False) -> None:
        """Write the process-local counters into the database."""
        if self.read_only or (not self._dirty and not force):
            return
        self._conn.execute("BEGIN IMMEDIATE")
        try:
            for name, value in self._local.items():
                self._conn.execute(
                    "INSERT INTO counters (name, value) VALUES (?, ?)"
                    " ON CONFLICT(name) DO UPDATE SET value = value + excluded.value",
                    (name, int(value)),
                )
            self._conn.execute("COMMIT")
        except sqlite3.Error:  # pragma: no cover - only on a hard IO error
            self._conn.execute("ROLLBACK")
            raise
        self._local = dict.fromkeys(_COUNTERS, 0)
        self._dirty = False

    # -- maintenance / reporting -------------------------------------------------------
    def stats(self) -> CacheStats:
        """Global counters across all processes that flushed into this file."""
        if self.read_only:
            rows = self._conn.execute("SELECT name, value FROM counters").fetchall()
        else:
            self.flush_counters()
            rows = self._conn.execute("SELECT name, value FROM counters").fetchall()
        counters = {row["name"]: int(row["value"]) for row in rows}
        entries = int(self._conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0])
        page_size = int(self._conn.execute("PRAGMA page_size").fetchone()[0])
        page_count = int(self._conn.execute("PRAGMA page_count").fetchone()[0])
        return CacheStats(
            hits=counters.get("hits", 0),
            misses=counters.get("misses", 0),
            writes=counters.get("writes", 0),
            entries=entries,
            size_bytes=page_size * page_count,
        )

    def count(self) -> int:
        """Number of cached analyses currently stored."""
        return int(self._conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0])

    def vacuum(self) -> None:
        """Reclaim space after a job deleted rows (no-op while other processes run)."""
        if not self.read_only:
            self._conn.execute("VACUUM")

    def prune_older_than(self, days: float) -> int:
        """Delete entries older than ``days``. Returns the number of deleted rows."""
        cutoff = time.time() - days * 86400.0
        cur = self._conn.execute("DELETE FROM analyses WHERE created_at < ?", (cutoff,))
        return cur.rowcount
