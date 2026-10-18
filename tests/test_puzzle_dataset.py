"""The puzzle-concept dataset builder and the concept trainer's helpers.

The scripts live in ``scripts/`` and import heavy modules lazily, so they are loaded by path
(the same pattern the other script tests use).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

from moveexp.config import THEME_VOCAB
from moveexp.data.lichess import Puzzle
from moveexp.model import build_puzzle_dataset

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


build = _load("build_puzzle_dataset")

START = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def _puzzle(themes=("fork",), moves=("e2e4", "e7e5", "g1f3")) -> Puzzle:
    return Puzzle(puzzle_id="p1", fen=START, moves=moves, rating=1500, themes=themes)


def test_rows_use_the_solver_move_and_the_mapped_targets():
    rows = build.rows_from_puzzles([_puzzle()])
    assert len(rows) == 1
    row = rows[0]
    assert row["move_uci"] == "e7e5"  # the solver is black, once e2e4 (the blunder) is applied
    assert row["label_source"] == "puzzle_tag" and row["source"] == "puzzle"
    assert len(row["theme_vector"]) == len(THEME_VOCAB)
    assert row["theme_vector"][THEME_VOCAB.index("fork")] == 1
    assert sum(row["theme_vector"]) == 1


def test_puzzles_without_a_mapped_tactic_are_skipped():
    # "opening"/"endgame" are phase tags, not tactics: nothing to map, so no training row.
    assert build.rows_from_puzzles([_puzzle(themes=("opening", "endgame"))]) == []


def test_all_solver_moves_emits_every_solver_ply():
    long_puzzle = _puzzle(moves=("e2e4", "e7e5", "g1f3", "b8c6", "f1b5"))
    assert len(build.rows_from_puzzles([long_puzzle])) == 1
    assert len(build.rows_from_puzzles([long_puzzle], all_solver_moves=True)) == 2


def test_build_puzzle_dataset_shapes_and_ids():
    rows = build.rows_from_puzzles([_puzzle(), _puzzle()])
    x, targets, ids = build_puzzle_dataset(rows)
    assert x.shape[0] == targets.shape[0] == len(ids) == 2
    assert targets.shape[1] == len(THEME_VOCAB)
    assert x.ndim == 4 and x.shape[2:] == (8, 8)
    assert ids == ["p1", "p1"]


def test_build_puzzle_dataset_rejects_empty_input():
    with pytest.raises(ValueError):
        build_puzzle_dataset([])


# ------------------------------------------------------------------ concept trainer helpers
torch = pytest.importorskip("torch")
concepts = _load("train_concepts")


def test_per_tag_prf_handles_unused_columns():
    y = np.array([[1, 0], [1, 0]], dtype=np.float32)
    scores = concepts.per_tag_prf(y, y)
    assert scores[0] == (1.0, 1.0, 1.0)
    assert scores[1] is None


def test_tune_global_threshold_prefers_a_separating_threshold():
    # Probabilities that are 0.9 for true positives and 0.1 elsewhere: any threshold in
    # (0.1, 0.9] gives a perfect macro F1.
    probs = np.array([[0.9, 0.1], [0.9, 0.1], [0.1, 0.9]], dtype=np.float32)
    truth = np.array([[1, 0], [1, 0], [0, 1]], dtype=np.float32)
    threshold, f1 = concepts.tune_global_threshold(probs, truth)
    assert f1 == 1.0
    assert 0.1 < threshold <= 0.9
