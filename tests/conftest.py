"""Shared pytest fixtures.

Engine-dependent tests are marked ``@pytest.mark.engine`` and skip automatically when no
Stockfish binary can be found. Set ``STOCKFISH_PATH`` to point at one, e.g.::

    STOCKFISH_PATH=/usr/games/stockfish pytest -m engine
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

import chess
import pytest

# Allow `pytest` to run from a clean checkout without `pip install -e .`.
_SRC = Path(__file__).resolve().parents[1] / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


def _find_stockfish() -> str | None:
    """Locate a Stockfish binary: ``STOCKFISH_PATH`` first, then ``PATH``."""
    env = os.environ.get("STOCKFISH_PATH")
    if env and (Path(env).is_file() or shutil.which(env)):
        return env
    return shutil.which("stockfish")


@pytest.fixture(scope="session")
def stockfish_path() -> str:
    """Path to a usable Stockfish, or skip the test."""
    path = _find_stockfish()
    if path is None:
        pytest.skip("no Stockfish binary found; set STOCKFISH_PATH to run engine tests")
    return path


@pytest.fixture
def engine_client(stockfish_path: str):
    """A running :class:`~moveexp.engine.client.StockfishClient` (no cache)."""
    from moveexp.engine.client import StockfishClient

    client = StockfishClient(stockfish_path, threads=1, hash_mb=32)
    with client:
        yield client


@pytest.fixture
def cache_db(tmp_path: Path) -> Path:
    """Path to a throw-away SQLite cache file."""
    return tmp_path / "engine_cache.sqlite3"


@pytest.fixture
def line_factory():
    """Build synthetic :class:`~moveexp.schema.LineInfo` objects without an engine.

    Every engine-dependent number in this project can be tested without Stockfish by
    constructing lines directly; only the parsing of raw UCI output needs the real thing.
    """
    from moveexp.schema import LineInfo

    def make(
        *,
        move: str | None = "e2e4",
        cp: float | None = 0.0,
        mate: int | None = None,
        rank: int = 1,
        turn: chess.Color = chess.WHITE,
        depth: int = 16,
        nodes: int = 1000,
        bound: str | None = None,
        pv: list[str] | None = None,
    ) -> LineInfo:
        return LineInfo(
            turn=turn,
            move=move,
            pv=pv if pv is not None else ([move] if move else []),
            score_cp=cp,
            mate=mate,
            depth=depth,
            nodes=nodes,
            multipv_rank=rank,
            bound=bound,
        )

    return make


@pytest.fixture
def start_board() -> chess.Board:
    """The initial position."""
    return chess.Board()


#: Horizontal mirror of a FEN: ranks reversed, piece colours swapped, side to move flipped.
_PIECE_SWAP = str.maketrans("PNBRQKpnbrqk", "pnbrqkPNBRQK")


def mirror_fen(fen: str) -> str:
    """Return the colour-flipped mirror of ``fen``.

    Used to check the perspective rule on mirrored positions: the evaluation from Black's
    point of view in the mirrored position must equal the negation of White's. Note that a
    mirrored position need not be *legal* (a knight that did not give check may give check
    after mirroring), so tests using this only rely on the piece placement, not on
    ``Board.is_valid()``.
    """
    placement, side, castling, ep, halfmove, fullmove = (fen.split() + ["-", "-", "0", "1"])[:6]
    ranks = [
        "".join(ch.translate(_PIECE_SWAP) for ch in rank[::-1]) for rank in placement.split("/")
    ]
    castling_mirrored = (
        "".join(sorted(castling.swapcase(), key="KQkq".index)) if castling != "-" else "-"
    )
    if ep != "-":
        file_idx = "abcdefgh".index(ep[0])
        rank_idx = int(ep[1])
        ep = f"{'abcdefgh'[7 - file_idx]}{9 - rank_idx}"
    new_side = "b" if side == "w" else "w"
    return f"{'/'.join(ranks)} {new_side} {castling_mirrored} {ep} {halfmove} {fullmove}"
