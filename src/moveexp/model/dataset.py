"""Dataset assembly and game-level splitting for the neural baseline.

Positions from one game are correlated, so the train/val/test split is made over whole
``game_id``s, never over individual rows (the same rule the project's Stage 3 plan uses).
This module is numpy-only so it can be exercised without torch.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

import numpy as np

from ..config import SPLIT_FRACTIONS
from ..schema import quality_to_index
from .encode import encode_board, n_planes


def build_dataset(
    rows: Iterable[Mapping[str, Any]],
    *,
    use_move: bool = True,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str]]:
    """Turn flat label rows into ``(X, quality, themes, game_ids)``.

    ``X`` is ``(n, channels, 8, 8)``; ``quality`` is an int class index per row; ``themes``
    is an ``(n, len(THEME_VOCAB))`` multi-hot matrix.
    """
    xs: list[np.ndarray] = []
    quality: list[int] = []
    themes: list[np.ndarray] = []
    game_ids: list[str] = []
    channels = n_planes(use_move)
    for row in rows:
        move = row["move_uci"] if use_move else None
        xs.append(encode_board(str(row["fen_before"]), move)[:channels])
        quality.append(quality_to_index(str(row["label"])))
        themes.append(np.asarray(row["theme_vector"], dtype=np.float32))
        game_ids.append(str(row["game_id"]))
    if not xs:
        raise ValueError("no rows to build a dataset from")
    return (
        np.stack(xs).astype(np.float32),
        np.asarray(quality, dtype=np.int64),
        np.stack(themes).astype(np.float32),
        game_ids,
    )


def build_intent_targets(rows: Iterable[Mapping[str, Any]]) -> np.ndarray:
    """Stack the ``intent_vector`` column into an ``(n, len(INTENT_VOCAB))`` matrix.

    Kept separate from :func:`build_dataset` so that function's signature stays stable;
    for the same input the row order (and therefore the alignment) is identical.
    """
    vectors = [np.asarray(row["intent_vector"], dtype=np.float32) for row in rows]
    if not vectors:
        raise ValueError("no rows to build intent targets from")
    return np.stack(vectors)


def build_puzzle_dataset(
    rows: Iterable[Mapping[str, Any]],
    *,
    use_move: bool = True,
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Turn flat puzzle rows into ``(X, theme_targets, puzzle_ids)``.

    The targets come from the Lichess puzzle tags (mapped onto ``THEME_VOCAB``), which are
    independent of this project's detectors -- so a model trained on them is measured against
    real ground truth rather than against our own rules. ``puzzle_ids`` group the rows (one
    puzzle can contribute several solver moves), so the split can be made per puzzle.
    """
    xs: list[np.ndarray] = []
    themes: list[np.ndarray] = []
    puzzle_ids: list[str] = []
    channels = n_planes(use_move)
    for row in rows:
        move = row["move_uci"] if use_move else None
        xs.append(encode_board(str(row["fen_before"]), move)[:channels])
        themes.append(np.asarray(row["theme_vector"], dtype=np.float32))
        puzzle_ids.append(str(row["puzzle_id"]))
    if not xs:
        raise ValueError("no rows to build a puzzle dataset from")
    return (
        np.stack(xs).astype(np.float32),
        np.stack(themes).astype(np.float32),
        puzzle_ids,
    )


def group_split(
    game_ids: list[str],
    *,
    seed: int = 20240917,
    fractions: Mapping[str, float] = SPLIT_FRACTIONS,
) -> dict[str, np.ndarray]:
    """Split row indices by game id into ``train``/``val``/``test`` index arrays."""
    unique = sorted(set(game_ids))
    rng = np.random.default_rng(seed)
    shuffled = [unique[i] for i in rng.permutation(len(unique))]

    n = len(shuffled)
    n_train = max(1, int(n * fractions["train"])) if n else 0
    n_val = max(1, int(n * fractions["val"])) if n >= 3 else 0
    train_games = set(shuffled[:n_train])
    val_games = set(shuffled[n_train : n_train + n_val])
    test_games = set(shuffled[n_train + n_val :])

    index = {"train": [], "val": [], "test": []}
    for row, game in enumerate(game_ids):
        if game in train_games:
            index["train"].append(row)
        elif game in val_games:
            index["val"].append(row)
        elif game in test_games:
            index["test"].append(row)
    return {name: np.asarray(idx, dtype=np.int64) for name, idx in index.items()}
