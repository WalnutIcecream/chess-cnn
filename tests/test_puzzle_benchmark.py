"""Tests for the puzzle benchmark's core logic (not the CSV reader).

The benchmark lives in ``eval/`` outside the package, so it is loaded by path here.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import chess

from positions import board

ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location(
    "puzzle_benchmark", ROOT / "eval" / "puzzle_benchmark.py"
)
bench = importlib.util.module_from_spec(_SPEC)
sys.modules["puzzle_benchmark"] = bench
assert _SPEC.loader is not None
_SPEC.loader.exec_module(bench)
bench.register_all()


def _fork_puzzle(themes: tuple[str, ...] = ("fork",)) -> bench.Puzzle:
    """Black to move (about to blunder with h6); white's Nf6 then forks king and rook."""
    b = board("wN@d5", "bR@e8", "bK@g8", "wK@g1", "bP@h7", turn=chess.BLACK)
    return bench.Puzzle(puzzle_id="1", fen=b.fen(), moves=("h7h6", "d5f6"), themes=themes)


def test_detected_themes_finds_the_fork():
    assert "fork" in bench.detected_themes(_fork_puzzle())


def test_evaluate_reports_perfect_fork_metrics():
    rows = {row["theme"]: row for row in bench.evaluate([_fork_puzzle()])}
    fork = rows["fork"]
    assert fork["tp"] == 1
    assert fork["fp"] == 0
    assert fork["fn"] == 0
    assert fork["precision"] == 1.0
    assert fork["recall"] == 1.0


def test_evaluate_counts_false_positives_and_negatives():
    # Gold says "pin" but the solution is a fork: a miss for pin, a false positive for fork.
    rows = {row["theme"]: row for row in bench.evaluate([_fork_puzzle(themes=("pin",))])}
    assert rows["pin"]["fn"] == 1 and rows["pin"]["recall"] == 0.0
    assert rows["fork"]["fp"] == 1 and rows["fork"]["precision"] == 0.0
