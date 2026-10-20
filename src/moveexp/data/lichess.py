"""Resumable download and streaming readers for the Lichess open database.

The exports are published under CC0 and are compressed with Zstandard, so the readers here
never unpack a file to disk: :func:`open_text` wraps the ``.zst`` stream in a text handle and
the parsers consume it line by line in constant memory. A 6-million-row puzzle CSV is read
the same way a 20-row fixture is.

Downloads use only the standard library (``urllib``) so this module adds no dependency; a
``Range`` request lets an interrupted download resume from ``<dest>.part`` instead of
starting over, and the finished file is moved into place atomically so a partial file is
never mistaken for a complete one.

Usage::

    from moveexp.data.lichess import download, PUZZLE_URL, stream_puzzles

    download(PUZZLE_URL, "data/raw/lichess_db_puzzle.csv.zst")   # resumable
    for puzzle in stream_puzzles("data/raw/lichess_db_puzzle.csv.zst"):
        ...
"""

from __future__ import annotations

import csv
import hashlib
import io
import shutil
import sys
import urllib.error
import urllib.request
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import IO

import chess

from ..schema import split_fen

__all__ = [
    "PUZZLE_URL",
    "Puzzle",
    "download",
    "format_puzzle_row",
    "iter_lines",
    "open_text",
    "reservoir_sample",
    "sha256_file",
    "stream_games",
    "stream_puzzles",
]

#: The full Lichess puzzle export: ~6.2M puzzles, rated and tagged, CC0. ~350 MB compressed.
PUZZLE_URL = "https://database.lichess.org/lichess_db_puzzle.csv.zst"

#: Column order of the puzzle CSV, as documented at https://database.lichess.org/.
PUZZLE_COLUMNS = (
    "PuzzleId",
    "FEN",
    "Moves",
    "Rating",
    "RatingDeviation",
    "Popularity",
    "NbPlays",
    "Themes",
    "GameUrl",
    "OpeningTags",
    "DailyDate",
)

_CHUNK = 1 << 20  # 1 MiB


# --------------------------------------------------------------------------------------
# Streaming text handle (transparent .zst decompression)
# --------------------------------------------------------------------------------------


@contextmanager
def open_text(path: str | Path) -> Iterator[IO[str]]:
    """Yield a text handle over ``path``, decompressing ``.zst`` on the fly.

    The decompressor is a stream, so memory use is a small window regardless of file size.
    A single ``close`` cascades through the wrapper stack to the underlying file.
    """
    path = Path(path)
    raw = path.open("rb")
    stream: IO[bytes] = raw
    if path.suffix == ".zst":
        import zstandard

        stream = zstandard.ZstdDecompressor().stream_reader(raw)  # type: ignore[assignment]
    text = io.TextIOWrapper(io.BufferedReader(stream), encoding="utf-8", newline="")
    try:
        yield text
    finally:
        text.close()


def iter_lines(path: str | Path) -> Iterator[str]:
    """Yield the lines of a (possibly ``.zst``) text file without the trailing newline."""
    with open_text(path) as handle:
        for line in handle:
            yield line.rstrip("\n")


# --------------------------------------------------------------------------------------
# Download
# --------------------------------------------------------------------------------------


def _human_bytes(count: float) -> str:
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if abs(count) < 1024.0 or unit == "TiB":
            return f"{count:.1f} {unit}"
        count /= 1024.0
    return f"{count:.1f} TiB"


def _remote_size(url: str, *, timeout: float) -> int | None:
    """Content-Length of ``url`` via a HEAD request, or ``None`` if the server hides it."""
    request = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            length = response.headers.get("Content-Length")
    except (urllib.error.URLError, OSError):
        return None
    return int(length) if length and length.isdigit() else None


def sha256_file(path: str | Path, *, chunk_size: int = _CHUNK) -> str:
    """Hex SHA-256 of a file, streamed so large files never load into memory."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(chunk_size), b""):
            digest.update(block)
    return digest.hexdigest()


def download(
    url: str,
    dest: str | Path,
    *,
    resume: bool = True,
    sha256: str | None = None,
    chunk_size: int = _CHUNK,
    timeout: float = 60.0,
    progress: bool = True,
) -> Path:
    """Download ``url`` to ``dest``, resuming a partial ``<dest>.part`` when possible.

    :param resume: continue a previous ``<dest>.part`` instead of restarting. If the server
        ignores the ``Range`` request the partial file is discarded and the download restarts.
    :param sha256: expected hex digest; when given, a mismatch raises before ``dest`` exists.
    :returns: ``dest`` once the file is complete and (if requested) verified.
    """
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        if sha256 is not None and sha256_file(dest) != sha256.lower():
            raise ValueError(f"{dest} exists but does not match the expected sha256")
        if progress:
            print(f"already present: {dest} ({_human_bytes(dest.stat().st_size)})", file=sys.stderr)
        return dest

    part = dest.with_name(dest.name + ".part")
    offset = part.stat().st_size if resume and part.exists() else 0

    headers = {"Range": f"bytes={offset}-"} if offset else {}
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        resumed = response.status == 206
        if offset and not resumed:
            # Server ignored the range: the body is the whole file, so start clean.
            offset = 0
        total = None
        length = response.headers.get("Content-Length")
        if length and length.isdigit():
            total = offset + int(length)
        elif (size := _remote_size(url, timeout=timeout)) is not None:
            total = size

        done = offset
        mode = "ab" if offset else "wb"
        with part.open(mode) as handle:
            while True:
                block = response.read(chunk_size)
                if not block:
                    break
                handle.write(block)
                done += len(block)
                if progress:
                    _print_progress(dest.name, done, total, resumed=bool(offset))

    if progress:
        print(file=sys.stderr)

    if sha256 is not None:
        actual = sha256_file(part)
        if actual != sha256.lower():
            part.unlink(missing_ok=True)
            raise ValueError(f"sha256 mismatch for {url}: expected {sha256}, got {actual}")

    part.replace(dest)
    if progress:
        print(f"downloaded {dest} ({_human_bytes(dest.stat().st_size)})", file=sys.stderr)
    return dest


def _print_progress(name: str, done: int, total: int | None, *, resumed: bool) -> None:
    prefix = "resuming" if resumed else "downloading"
    if total:
        pct = 100.0 * done / total
        message = f"\r{prefix} {name}: {_human_bytes(done)} / {_human_bytes(total)} ({pct:5.1f}%)"
    else:
        message = f"\r{prefix} {name}: {_human_bytes(done)}"
    sys.stderr.write(message)
    sys.stderr.flush()


# --------------------------------------------------------------------------------------
# Puzzles
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Puzzle:
    """One Lichess puzzle, reduced to the fields a benchmark or dataset needs.

    The FEN is the position *before* the opponent's blunder; ``moves[0]`` is that blunder
    (which creates the puzzle) and the solution starts at ``moves[1]``. Every solver move is
    an only-move: any other move considerably worsens the position.
    """

    puzzle_id: str
    fen: str
    moves: tuple[str, ...]
    rating: int = 0
    rating_deviation: int = 0
    popularity: int = 0
    nb_plays: int = 0
    themes: tuple[str, ...] = ()
    game_url: str = ""
    opening_tags: tuple[str, ...] = ()
    daily_date: int | None = None

    def board(self) -> chess.Board:
        """The position before the opponent's blunder, tolerating counterless FENs."""
        try:
            return chess.Board(self.fen.strip())
        except ValueError:
            placement, side, castling, ep, halfmove, fullmove = split_fen(self.fen)
            return chess.Board(f"{placement} {side} {castling} {ep} {halfmove} {fullmove}")

    def uci_moves(self) -> tuple[chess.Move, ...]:
        """Every move of the puzzle as :class:`chess.Move` (blunder first)."""
        return tuple(chess.Move.from_uci(uci) for uci in self.moves)

    def solution_moves(self) -> tuple[chess.Move, ...]:
        """The solver's line, i.e. the moves after the opponent's blunder."""
        return self.uci_moves()[1:]

    def position_after_blunder(self) -> chess.Board:
        """The board the solver actually faces (blunder applied).

        :raises ValueError: if the recorded blunder is not legal in the FEN.
        """
        board = self.board()
        blunder = self.uci_moves()[0]
        if blunder not in board.legal_moves:
            raise ValueError(f"puzzle {self.puzzle_id}: blunder {blunder} not legal in {self.fen}")
        board.push(blunder)
        return board


def _to_int(value: str | None) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0


def parse_puzzle_row(row: dict[str, str]) -> Puzzle | None:
    """Turn one CSV row into a :class:`Puzzle`, or ``None`` when it is unusable."""
    fen = (row.get("FEN") or "").strip()
    moves = (row.get("Moves") or "").split()
    if not fen or len(moves) < 2:
        return None
    daily = (row.get("DailyDate") or "").strip()
    return Puzzle(
        puzzle_id=(row.get("PuzzleId") or "").strip(),
        fen=fen,
        moves=tuple(moves),
        rating=_to_int(row.get("Rating")),
        rating_deviation=_to_int(row.get("RatingDeviation")),
        popularity=_to_int(row.get("Popularity")),
        nb_plays=_to_int(row.get("NbPlays")),
        themes=tuple((row.get("Themes") or "").split()),
        game_url=(row.get("GameUrl") or "").strip(),
        opening_tags=tuple((row.get("OpeningTags") or "").split()),
        daily_date=int(daily) if daily.isdigit() else None,
    )


def stream_puzzles(path: str | Path) -> Iterator[Puzzle]:
    """Stream :class:`Puzzle` records from a puzzle CSV (plain or ``.zst``)."""
    with open_text(path) as handle:
        header = handle.readline()
        if not header:
            return
        names = next(csv.reader([header]))
        for raw in csv.DictReader(handle, fieldnames=names):
            puzzle = parse_puzzle_row(raw)
            if puzzle is not None:
                yield puzzle


def format_puzzle_row(puzzle: Puzzle) -> list[str]:
    """The puzzle as CSV fields in :data:`PUZZLE_COLUMNS` order (inverse of the parser).

    Round-trips through :func:`parse_puzzle_row`, which is what lets the committed test
    fixture be produced by a script and read back by exactly the same code path as the real
    corpus.
    """
    return [
        puzzle.puzzle_id,
        puzzle.fen,
        " ".join(puzzle.moves),
        str(puzzle.rating),
        str(puzzle.rating_deviation),
        str(puzzle.popularity),
        str(puzzle.nb_plays),
        " ".join(puzzle.themes),
        puzzle.game_url,
        " ".join(puzzle.opening_tags),
        "" if puzzle.daily_date is None else str(puzzle.daily_date),
    ]


def reservoir_sample(items: Iterable[object], n: int, *, seed: int = 0) -> list:
    """Uniformly sample ``n`` items from a stream in constant memory (reservoir sampling).

    The corpus is ordered (oldest puzzles first), so taking the first ``n`` would bias the
    sample towards early, often weaker puzzles. One pass with a fixed seed gives a
    representative, reproducible subset without holding the corpus in memory.
    """
    import random

    rng = random.Random(seed)
    sample: list = []
    for seen, item in enumerate(items):
        if len(sample) < n:
            sample.append(item)
        else:
            slot = rng.randint(0, seen)
            if slot < n:
                sample[slot] = item
    return sample


# --------------------------------------------------------------------------------------
# Games
# --------------------------------------------------------------------------------------


def stream_games(path: str | Path) -> Iterator[chess.pgn.Game]:
    """Stream PGN games from a ``.pgn`` or ``.pgn.zst`` file (constant memory)."""
    import chess.pgn

    with open_text(path) as handle:
        while (game := chess.pgn.read_game(handle)) is not None:
            yield game


def copy_file(source: str | Path, dest: str | Path) -> Path:
    """Copy ``source`` to ``dest``, creating parents (used by tests and fixtures)."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, dest)
    return dest
