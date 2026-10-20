"""The stratified fixture sampler.

``scripts/make_puzzle_fixture.py`` builds the committed offline fixture, so its sampling has to
be right or every later regression test is measured against the wrong thing. Loaded by path
(the script lives in ``scripts/``).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from moveexp.data.lichess import Puzzle

ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location(
    "make_puzzle_fixture", ROOT / "scripts" / "make_puzzle_fixture.py"
)
assert _SPEC is not None and _SPEC.loader is not None
fixture = importlib.util.module_from_spec(_SPEC)
sys.modules["make_puzzle_fixture"] = fixture
_SPEC.loader.exec_module(fixture)

START = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def _puzzle(puzzle_id: str, themes: tuple[str, ...]) -> Puzzle:
    return Puzzle(puzzle_id=puzzle_id, fen=START, moves=("e2e4", "e7e5"), themes=themes)


def test_stratified_sample_caps_each_theme():
    puzzles = [_puzzle(f"p{i}", ("fork",)) for i in range(50)]
    assert len(fixture.stratified_sample(puzzles, per_theme=5)) == 5


def test_stratified_sample_keeps_a_puzzle_no_random_sample_would_reach():
    # One rare puzzle behind fifty common ones: stratification must still surface it, which is
    # the whole reason the fixture is not a plain random sample.
    puzzles = [_puzzle(f"a{i}", ("fork",)) for i in range(50)] + [_puzzle("rare", ("enPassant",))]
    ids = {p.puzzle_id for p in fixture.stratified_sample(puzzles, per_theme=3)}
    assert "rare" in ids


def test_stratified_sample_is_deterministic_and_sorted():
    puzzles = [_puzzle(f"p{i:02d}", ("fork", "pin")) for i in range(30)]
    first = [p.puzzle_id for p in fixture.stratified_sample(puzzles, per_theme=4, seed=1)]
    second = [p.puzzle_id for p in fixture.stratified_sample(puzzles, per_theme=4, seed=1)]
    assert first == second == sorted(first)


def test_stratified_sample_ignores_puzzles_without_mapped_themes():
    assert fixture.stratified_sample([_puzzle("x", ("opening", "endgame"))], per_theme=5) == []


def test_stratified_sample_deduplicates_puzzles_tagged_with_several_themes():
    one = _puzzle("both", ("fork", "pin"))
    sample = fixture.stratified_sample([one], per_theme=5)
    assert [p.puzzle_id for p in sample] == ["both"]
