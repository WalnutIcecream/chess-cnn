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
from moveexp.model import augment_planes, build_puzzle_dataset
from moveexp.model.metrics import multilabel_macro_f1

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


# ------------------------------------------------------------------ rating bands, groups, dedupe
def test_rating_band_fills_the_range_without_gaps():
    assert build.rating_band(1000) == "<1200"
    assert build.rating_band(1199) == "<1200"
    assert build.rating_band(1200) == "1200-1599"
    assert build.rating_band(2399) == "2000-2399"
    assert build.rating_band(2400) == "2400+"
    assert build.rating_band(3000) == "2400+"


def test_rating_bands_sort_low_to_high():
    bands = [build.rating_band(rating) for rating in (900, 1300, 1700, 2100, 2600)]
    assert sorted(bands, key=build._band_order) == bands


def test_tag_groups_reports_which_groups_a_rows_themes_belong_to():
    assert build.tag_groups(["fork"]) == "move"
    assert build.tag_groups(["zugzwang"]) == "puzzle"
    assert build.tag_groups(["fork", "zugzwang"]) == "move puzzle"
    assert build.tag_groups([]) == ""


def test_rows_record_the_rating_band_and_tag_groups():
    row = build.rows_from_puzzles([_puzzle()])[0]  # rating 1500, tagged "fork"
    assert row["rating_band"] == "1200-1599"
    assert row["tag_groups"] == "move"

    puzzle_level = build.rows_from_puzzles([_puzzle(themes=("zugzwang",))])[0]
    assert puzzle_level["tag_groups"] == "puzzle"


def test_dedupe_by_position_keeps_the_first_row_for_each_position():
    rows = [
        {"fen_before": START, "move_uci": "e2e4"},
        {"fen_before": START, "move_uci": "d2d4"},
        {"fen_before": "8/8/8/8/8/8/8/K6k w - - 0 1", "move_uci": "a1a2"},
    ]
    kept = build.dedupe_by_position(rows)
    assert [row["move_uci"] for row in kept] == ["e2e4", "a1a2"]


def test_dedupe_by_position_ignores_the_move_counters():
    rows = [
        {"fen_before": "8/8/8/8/8/8/8/K6k w - - 0 1"},
        {"fen_before": "8/8/8/8/8/8/8/K6k w - - 9 40"},
    ]
    assert len(build.dedupe_by_position(rows)) == 1


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


def test_top_k_baseline_predicts_exactly_the_k_most_common_tags():
    train = np.array([[1, 1, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0]], dtype=np.float32)
    out = concepts.top_k_baseline(train, n_rows=3, k=2)
    assert out.shape == (3, 3)
    assert out[:, 0].sum() == 3  # the most common tag, on every row
    assert out[:, 1].sum() == 3  # the second most common
    assert out[:, 2].sum() == 0  # never observed in training: never predicted


def test_tune_top_k_returns_the_best_k_it_found():
    train = np.array([[1, 1, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0]], dtype=np.float32)
    k, score = concepts.tune_top_k(train, train, max_k=3)
    best = max(
        concepts.multilabel_micro_f1(train, concepts.top_k_baseline(train, len(train), kk))
        for kk in range(1, 4)
    )
    assert 1 <= k <= 3
    assert score == best


def test_per_tag_thresholds_leave_an_unseen_tag_neutral():
    probs = np.array([[0.9, 0.1]], dtype=np.float32)
    truth = np.array([[1, 0]], dtype=np.float32)
    thresholds = concepts.tune_per_tag_thresholds(probs, truth)
    # Column 1 has no positive: it must not be tuned to the bottom of the grid.
    assert thresholds[1] == 0.5


def test_per_tag_thresholds_beat_a_single_global_one_when_tags_are_scaled_apart():
    """The fix this item exists for: rare tags need their own threshold."""
    n = 400
    truth = np.zeros((n, 2), dtype=np.float32)
    truth[:200, 0] = 1.0  # a common tag
    truth[:20, 1] = 1.0  # a rare one
    probs = np.zeros((n, 2), dtype=np.float32)
    probs[:200, 0], probs[200:, 0] = 0.9, 0.6
    probs[:20, 1], probs[20:, 1] = 0.5, 0.1

    per_tag = concepts.apply_per_tag_thresholds(
        probs, concepts.tune_per_tag_thresholds(probs, truth)
    )
    assert multilabel_macro_f1(truth, per_tag) == 1.0

    # No single value clears 0.6 for the common tag while staying at or below 0.5 for the rare
    # one, so the global threshold has to compromise somewhere.
    _t, global_f1 = concepts.tune_global_threshold(probs, truth)
    assert global_f1 < 1.0


# ------------------------------------------------------------------ augmentation + schedule
def test_torch_batch_transform_matches_the_numpy_reference():
    x = np.random.default_rng(0).random((4, 15, 8, 8)).astype(np.float32)
    tensor = torch.from_numpy(x)
    for mirror in (False, True):
        for switch in (False, True):
            got = concepts.transform_batch(tensor, mirror=mirror, switch_colour=switch).numpy()
            want = np.stack([augment_planes(row, mirror=mirror, switch_colour=switch) for row in x])
            assert np.allclose(got, want)


def test_augment_batch_is_deterministic_and_conserves_pieces():
    x = torch.zeros(8, 15, 8, 8)
    x[:, 0, 7, 0] = 1.0  # a piece on a1 in every sample
    first = concepts.augment_batch(x, np.random.default_rng(1))
    second = concepts.augment_batch(x, np.random.default_rng(1))
    assert torch.equal(first, second)
    assert first.shape == x.shape
    assert torch.allclose(first[:, :12].sum(dim=(1, 2, 3)), x[:, :12].sum(dim=(1, 2, 3)))


def test_cosine_lr_runs_from_the_base_rate_to_the_floor_without_rising():
    rates = [concepts.cosine_lr(1e-3, epoch, 10) for epoch in range(10)]
    assert rates[0] == pytest.approx(1e-3)
    assert rates[-1] == pytest.approx(1e-3 * 0.05)
    assert all(later <= earlier for earlier, later in zip(rates, rates[1:], strict=False))
    assert concepts.cosine_lr(1e-3, 0, 1) == 1e-3  # one epoch: nothing to decay


def test_train_concepts_runs_end_to_end_on_a_tiny_dataset(tmp_path):
    import pandas as pd

    start = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    rows = []
    for index in range(40):
        vector = [0] * len(THEME_VOCAB)
        vector[THEME_VOCAB.index("fork")] = 1
        if index % 3 == 0:
            vector[THEME_VOCAB.index("pin")] = 1
        rows.append(
            {
                "puzzle_id": f"p{index % 12}",
                "fen_before": start,
                "move_uci": "e2e4",
                "theme_vector": vector,
            }
        )
    labels = tmp_path / "tiny.parquet"
    pd.DataFrame(rows).to_parquet(labels, index=False)

    out = tmp_path / "out.csv"
    code = concepts.main(
        ["--labels", str(labels), "--epochs", "1", "--out", str(out), "--overwrite"]
    )
    assert code == 0
    header, *body = out.read_text().splitlines()
    assert "model_per_tag" in header and "topk_baseline" in header and "augment" in header
    assert len(body) == 2  # one micro_f1 row and one macro_f1 row
