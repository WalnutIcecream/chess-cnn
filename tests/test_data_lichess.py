"""Download and streaming readers for the Lichess open database.

The puzzle fixtures are written at test time by compressing a few CSV rows with
``zstandard`` -- no binary fixture is committed, and the streaming path (``.zst``) is
exercised for real. Downloads are tested against a fake ``urlopen`` so the resume logic
(``Range`` -> 206, a server that ignores the range -> 200) is pinned without a network.
"""

from __future__ import annotations

from pathlib import Path

import chess
import pytest
import zstandard

from moveexp.data.lichess import (
    Puzzle,
    download,
    iter_lines,
    open_text,
    parse_puzzle_row,
    sha256_file,
    stream_games,
    stream_puzzles,
)

PUZZLE_CSV = (
    "PuzzleId,FEN,Moves,Rating,RatingDeviation,Popularity,NbPlays,Themes,GameUrl,"
    "OpeningTags,DailyDate\n"
    "00sHx,q3k1nr/1pp1nQpp/3p4/1P2p3/4P3/B1PP1b2/B5PP/5K2 b k - 0 17,"
    "e8d7 a2e6 d7d8 f7f8,1760,80,83,72,mate mateIn2 middlegame short,"
    "https://lichess.org/yyznGmXs/black#34,Italian_Game,"
    "\n"
    "00sJ9,r3r1k1/p4ppp/2p2n2/1p6/3P1qb1/2NQR3/PPB2PP1/R1B3K1 w - - 5 18,"
    "e3g3 e8e1 g1h2 e1c1 a1c1 f4h6 h2g1 h6c1,2671,105,87,325,"
    "advantage attraction fork middlegame sacrifice veryLong,"
    "https://lichess.org/gyFeQsOE#35,French_Defense,1607774862751\n"
)

PGN = (
    '[Event "Test"]\n[Site "?"]\n[White "A"]\n[Black "B"]\n[Result "1-0"]\n\n'
    "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 1-0\n"
)


def _write(path: Path, text: str, *, zst: bool = True) -> Path:
    data = text.encode("utf-8")
    path.write_bytes(zstandard.ZstdCompressor().compress(data) if zst else data)
    return path


# --------------------------------------------------------------------------- streaming
def test_stream_puzzles_reads_a_zst_file(tmp_path: Path):
    path = _write(tmp_path / "puzzles.csv.zst", PUZZLE_CSV)
    puzzles = list(stream_puzzles(path))
    assert [p.puzzle_id for p in puzzles] == ["00sHx", "00sJ9"]
    first = puzzles[0]
    assert first.rating == 1760 and first.popularity == 83 and first.nb_plays == 72
    assert first.themes == ("mate", "mateIn2", "middlegame", "short")
    assert first.opening_tags == ("Italian_Game",)
    assert first.daily_date is None  # empty field
    assert puzzles[1].daily_date == 1607774862751


def test_stream_puzzles_reads_a_plain_csv(tmp_path: Path):
    path = _write(tmp_path / "puzzles.csv", PUZZLE_CSV, zst=False)
    assert len(list(stream_puzzles(path))) == 2


def test_iter_lines_and_open_text_handle_both_encodings(tmp_path: Path):
    zst = _write(tmp_path / "a.txt.zst", "one\ntwo\n")
    plain = _write(tmp_path / "a.txt", "one\ntwo\n", zst=False)
    assert list(iter_lines(zst)) == ["one", "two"]
    assert list(iter_lines(plain)) == ["one", "two"]
    with open_text(zst) as handle:
        assert handle.readline() == "one\n"


def test_stream_games_reads_pgn_zst(tmp_path: Path):
    path = _write(tmp_path / "games.pgn.zst", PGN)
    games = list(stream_games(path))
    assert len(games) == 1
    assert len(list(games[0].mainline_moves())) == 6


# --------------------------------------------------------------------------- parsing
def test_parse_puzzle_row_rejects_a_row_without_a_move_list():
    assert parse_puzzle_row({"FEN": "8/8/8/8/8/8/8/K6k w - - 0 1", "Moves": "a1a2"}) is None
    assert parse_puzzle_row({"FEN": "", "Moves": "a1a2 a2a3"}) is None


def test_puzzle_helpers_walk_the_solution():
    puzzle = Puzzle(
        puzzle_id="x",
        fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        moves=("e2e4", "e7e5", "g1f3"),
        themes=("fork",),
    )
    assert len(puzzle.uci_moves()) == 3
    assert [m.uci() for m in puzzle.solution_moves()] == ["e7e5", "g1f3"]
    board = puzzle.position_after_blunder()
    assert board.turn == chess.BLACK
    assert board.piece_at(chess.E4) == chess.Piece(chess.PAWN, chess.WHITE)


def test_puzzle_board_tolerates_a_counterless_fen():
    puzzle = Puzzle(puzzle_id="x", fen="8/8/8/8/8/8/8/K6k w - -", moves=("a1a2", "h1h2"))
    assert puzzle.board().turn == chess.WHITE


# --------------------------------------------------------------------------- download
class _FakeResponse:
    """Minimal stand-in for the ``urlopen`` result, honouring an optional ``Range``."""

    def __init__(self, data: bytes, start: int, *, honour_range: bool) -> None:
        self._body = data[start:] if (start and honour_range) else data
        self._pos = 0
        self.status = 206 if (start and honour_range) else 200
        self.headers = {"Content-Length": str(len(self._body))}

    def read(self, n: int = -1) -> bytes:
        if n is None or n < 0:
            n = len(self._body) - self._pos
        chunk = self._body[self._pos : self._pos + n]
        self._pos += len(chunk)
        return chunk

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *exc: object) -> bool:
        return False


def _patch_urlopen(monkeypatch: pytest.MonkeyPatch, data: bytes, *, honour_range: bool):
    def fake_urlopen(request, timeout=None):  # noqa: ANN001 - mirrors urlopen signature
        header = request.get_header("Range")
        start = int(header.split("=")[1].split("-")[0]) if header else 0
        return _FakeResponse(data, start, honour_range=honour_range)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)


def test_download_writes_the_file_and_removes_the_part(tmp_path, monkeypatch):
    data = b"hello world" * 100
    _patch_urlopen(monkeypatch, data, honour_range=True)
    dest = download("https://example.test/f", tmp_path / "f", progress=False)
    assert dest.read_bytes() == data
    assert not (tmp_path / "f.part").exists()


def test_download_resumes_from_a_partial_file(tmp_path, monkeypatch):
    data = b"0123456789" * 100
    dest = tmp_path / "f"
    part = tmp_path / "f.part"
    part.write_bytes(data[:137])  # a previous run got part way
    _patch_urlopen(monkeypatch, data, honour_range=True)
    download("https://example.test/f", dest, progress=False)
    assert dest.read_bytes() == data
    assert not part.exists()


def test_download_restarts_when_the_server_ignores_the_range(tmp_path, monkeypatch):
    data = b"abcdefghij" * 50
    part = tmp_path / "f.part"
    part.write_bytes(b"stale content from an older file")
    _patch_urlopen(monkeypatch, data, honour_range=False)
    dest = download("https://example.test/f", tmp_path / "f", progress=False)
    assert dest.read_bytes() == data


def test_download_verifies_sha256_and_leaves_nothing_on_mismatch(tmp_path, monkeypatch):
    data = b"payload"
    _patch_urlopen(monkeypatch, data, honour_range=True)
    with pytest.raises(ValueError, match="sha256"):
        download("https://example.test/f", tmp_path / "f", sha256="00" * 32, progress=False)
    assert not (tmp_path / "f").exists()
    assert not (tmp_path / "f.part").exists()


def test_download_accepts_a_matching_sha256(tmp_path, monkeypatch):
    data = b"payload"
    digest = sha256_file(_write(tmp_path / "src", "payload", zst=False))
    _patch_urlopen(monkeypatch, data, honour_range=True)
    dest = download("https://example.test/f", tmp_path / "f", sha256=digest, progress=False)
    assert dest.read_bytes() == data


def test_download_is_a_no_op_when_the_file_already_exists(tmp_path, monkeypatch):
    dest = tmp_path / "f"
    dest.write_bytes(b"already here")
    monkeypatch.setattr(
        "urllib.request.urlopen", lambda *a, **k: pytest.fail("network should not be touched")
    )
    assert download("https://example.test/f", dest, progress=False) == dest
