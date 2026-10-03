"""CLI surface tests: argument handling, output shape, and the cache round-trip.

The engine-backed test is marked ``engine`` (it needs a real Stockfish binary); everything
else runs anywhere.
"""

from __future__ import annotations

import json

import chess
import pytest
from typer.testing import CliRunner

from moveexp.cli import _resolve_move, app
from moveexp.config import INTENT_VOCAB, QUALITY_LABELS, THEME_VOCAB

runner = CliRunner()

FEN_SCHOLARS_MATE = "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 4 4"


# ------------------------------------------------------------------------ engine-free
def test_vocab_command_prints_the_frozen_vocabularies():
    result = runner.invoke(app, ["vocab"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["quality_labels"] == list(QUALITY_LABELS)
    assert payload["theme_vocab"] == list(THEME_VOCAB)
    assert payload["theme_vocab_size"] == len(THEME_VOCAB)
    assert len(set(THEME_VOCAB)) == len(THEME_VOCAB), "the vocabulary must be a set"
    assert len(set(INTENT_VOCAB)) == len(INTENT_VOCAB)
    assert not set(QUALITY_LABELS) & set(THEME_VOCAB), "vocabularies must not overlap"


def test_help_lists_both_commands():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "analyze-move" in result.stdout
    assert "vocab" in result.stdout


@pytest.mark.parametrize("text", ["Qxf7#", "f3f7"])
def test_move_is_accepted_as_san_or_uci(text: str):
    move = _resolve_move(chess.Board(FEN_SCHOLARS_MATE), text)
    assert move.uci() == "f3f7"


@pytest.mark.parametrize("text", ["e2e4", "Kd5", "not-a-move"])
def test_illegal_or_unparseable_moves_are_rejected(text: str):
    with pytest.raises(Exception) as excinfo:
        _resolve_move(chess.Board(FEN_SCHOLARS_MATE), text)
    assert "legal" in str(excinfo.value)


def test_invalid_fen_is_a_clean_cli_error_not_a_traceback():
    result = runner.invoke(
        app, ["--engine-path", "unused", "analyze-move", "--fen", "not a fen", "--move", "e2e4"]
    )
    assert result.exit_code != 0
    assert result.exception is None or isinstance(result.exception, SystemExit)


# ------------------------------------------------------------------------ engine-backed
@pytest.mark.engine
def test_analyze_move_reports_engine_metadata_and_uses_the_cache(tmp_path, stockfish_path: str):
    """A second identical run must be served from the SQLite cache and say so."""
    cache_db = tmp_path / "cache.sqlite3"
    args = [
        "--engine-path",
        stockfish_path,
        "analyze-move",
        "--fen",
        FEN_SCHOLARS_MATE,
        "--move",
        "f3f7",
        "--depth",
        "12",
        "--multipv",
        "3",
        "--cache-db",
        str(cache_db),
    ]
    first = runner.invoke(app, args)
    assert first.exit_code == 0, first.output
    report = json.loads(first.stdout)
    assert report["move_san"] == "Qxf7#"
    assert report["quality"]["label"] == "great"  # mate, the only good move
    assert report["quality"]["is_critical"] is True
    assert report["meta"]["limit_signature"] == "d12"
    assert report["meta"]["cache_hit"] is False, "nothing was cached before this run"
    assert "Stockfish" in report["meta"]["engine_id"], "the engine's own name must be recorded"
    assert "Stockfish" in report["provenance"]["engine_name"], "provenance must record the engine"
    assert report["provenance"]["limit_type"] == "depth"
    assert report["provenance"]["limit_value"] == 12

    assert cache_db.is_file()
    second = runner.invoke(app, args)
    assert second.exit_code == 0, second.output
    assert json.loads(second.stdout)["meta"]["cache_hit"] is True
    # A different depth is a different question, so it must not be served from that cache.
    other = runner.invoke(app, [*args[:8], "13", *args[9:]])
    assert other.exit_code == 0, other.output
    assert json.loads(other.stdout)["meta"]["cache_hit"] is False


@pytest.mark.engine
def test_no_cache_flag_bypasses_a_warm_cache(tmp_path, stockfish_path: str):
    cache_db = tmp_path / "cache.sqlite3"
    args = [
        "--engine-path",
        stockfish_path,
        "analyze-move",
        "--fen",
        FEN_SCHOLARS_MATE,
        "--move",
        "Qxf7#",
        "--depth",
        "10",
        "--cache-db",
        str(cache_db),
    ]
    assert runner.invoke(app, args).exit_code == 0
    bypassed = runner.invoke(app, [*args, "--no-cache"])
    assert bypassed.exit_code == 0, bypassed.output
    assert json.loads(bypassed.stdout)["meta"]["cache_hit"] is False


@pytest.mark.engine
def test_report_can_be_written_to_a_file(tmp_path, stockfish_path: str):
    out = tmp_path / "nested" / "report.json"
    result = runner.invoke(
        app,
        [
            "--engine-path",
            stockfish_path,
            "analyze-move",
            "--fen",
            FEN_SCHOLARS_MATE,
            "--move",
            "Qxf7#",
            "--depth",
            "10",
            "--no-cache",
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(out.read_text())["move_uci"] == "f3f7"
