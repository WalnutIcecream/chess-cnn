"""Tests for the puzzle benchmark's core logic and its grouped report.

Two things are pinned here: the aggregation arithmetic, and the claim the group split exists
to encode -- that move-level motifs are measurable from a position while puzzle-level
descriptions are not. The second runs against the committed fixture
(``tests/data/puzzles_sample.csv``) so it works with no corpus and no network.

The fixture is regenerated with::

    python scripts/make_puzzle_fixture.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import chess
import pytest

from moveexp.data import puzzle_themes as pt
from positions import board

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "data" / "puzzles_sample.csv"
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


# ------------------------------------------------------------------ grouped reporting
def test_every_theme_row_carries_its_group():
    rows = {row["theme"]: row for row in bench.evaluate([_fork_puzzle()])}
    assert rows["fork"]["group"] == "move"


def test_group_scores_pools_counts_and_averages_f1():
    rows = [
        {"group": "move", "tp": 3, "fp": 1, "fn": 0, "f1": 0.5},
        {"group": "move", "tp": 0, "fp": 0, "fn": 2, "f1": 0.0},
        {"group": "puzzle", "tp": 1, "fp": 1, "fn": 1, "f1": 0.5},
    ]
    scores = bench.group_scores(rows)
    move = scores["move"]
    assert (move["tp"], move["fp"], move["fn"]) == (3, 1, 2)
    assert move["macro_f1"] == 0.25  # mean of the two per-theme F1 values
    assert move["micro_f1"] == round(2 * 0.75 * 0.6 / (0.75 + 0.6), 4)
    assert scores["puzzle"]["micro_f1"] == round(2 * 0.5 * 0.5 / 1.0, 4)


# ------------------------------------------------------------------ the committed fixture
def _fixture_puzzles():
    return list(bench.stream_puzzles(FIXTURE))


def test_fixture_covers_both_groups():
    puzzles = _fixture_puzzles()
    assert len(puzzles) > 100
    themes: set[str] = set()
    for puzzle in puzzles:
        themes.update(pt.themes_from_tags(puzzle.themes))
    assert themes & pt.MOVE_LEVEL_THEMES
    assert themes & pt.PUZZLE_LEVEL_THEMES


def test_move_level_detectors_beat_puzzle_level_on_the_fixture():
    """The hypothesis the split encodes, checked offline against the committed fixture."""
    scores = bench.group_scores(bench.evaluate(_fixture_puzzles()))
    assert scores["move"]["macro_f1"] > scores["puzzle"]["macro_f1"]


# ------------------------------------------------------------------ regression guard
#: Measured on the committed fixture after the loop-item-5 rewrites, as
#: ``(minimum F1, maximum detections)``. The floor catches a good detector being broken; the
#: ceiling catches an over-firing one reverting. Both are needed here: for the three rewritten
#: detectors an F1 floor alone would be met by the *old* definitions, because their precision is
#: low for a structural reason (the tag marks the puzzle's point, not merely a decidable motif).
#: Each ceiling sits below the pre-rewrite count (x-ray 198, interference 51, hanging 222), so a
#: revert fails.
DETECTOR_EXPECTATIONS = {
    "promotion": (0.95, 60),
    "smothered_mate": (0.95, 30),
    "en_passant": (0.95, 30),
    "double_check": (0.90, 35),
    "advanced_pawn": (0.65, 100),
    "x_ray": (0.03, 180),
    "hanging_piece": (0.07, 210),
    "interference": (0.00, 30),
}


@pytest.fixture(scope="module")
def fixture_rows():
    """Per-theme benchmark rows for the fixture, evaluated once for the whole module."""
    return {row["theme"]: row for row in bench.evaluate(_fixture_puzzles())}


def test_detector_expectations_hold_on_the_fixture(fixture_rows):
    for theme, (min_f1, max_detected) in DETECTOR_EXPECTATIONS.items():
        row = fixture_rows[theme]
        assert row["f1"] >= min_f1, f"{theme}: F1 regressed to {row['f1']}"
        assert row["detected"] <= max_detected, f"{theme}: over-firing ({row['detected']} hits)"


def test_wing_attacks_are_measured_without_being_chased(fixture_rows):
    """Kingside/queenside attack are puzzle-level tags: reported, deliberately not tuned.

    Item 5's rule is to fix definitions that are wrong, not to chase labels that are
    mismatched. This pins that decision: the detectors stay measurable, and the tag stays
    classified as puzzle-level, so a future change has to argue with both.
    """
    for theme in ("kingside_attack", "queenside_attack"):
        assert fixture_rows[theme]["gold"] > 0
        assert pt.theme_group(theme) == "puzzle"
