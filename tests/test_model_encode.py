"""Tests for the neural baseline's encoder and dataset helpers (no torch required)."""

from __future__ import annotations

import pytest

from moveexp.config import THEME_VOCAB
from moveexp.model import N_PLANES, build_dataset, encode_board, group_split, n_planes

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
BLACK_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1"


def test_shape_piece_and_side_planes() -> None:
    x = encode_board(START_FEN)
    assert x.shape == (N_PLANES, 8, 8)
    assert x[:12].sum() == 32.0  # 32 pieces
    assert x[12].sum() == 64.0  # white to move: whole side plane set
    assert x[13].sum() == 0.0 and x[14].sum() == 0.0  # no move given


def test_move_planes_mark_from_and_to_squares() -> None:
    x = encode_board(START_FEN, "e2e4")
    assert x[13].sum() == 1.0 and x[14].sum() == 1.0
    assert x[13, 6, 4] == 1.0  # e2 -> row 6, file 4
    assert x[14, 4, 4] == 1.0  # e4 -> row 4, file 4


def test_black_side_to_move_plane_is_empty() -> None:
    assert encode_board(BLACK_FEN)[12].sum() == 0.0


def test_illegal_move_uci_is_ignored() -> None:
    x = encode_board(START_FEN, "not-a-move")
    assert x[13].sum() == 0.0 and x[14].sum() == 0.0


def _row(game_id: str, move: str = "e2e4", label: str = "best") -> dict:
    return {
        "game_id": game_id,
        "fen_before": START_FEN,
        "move_uci": move,
        "label": label,
        "theme_vector": [0] * len(THEME_VOCAB),
    }


def test_build_dataset_shapes() -> None:
    x, y, themes, game_ids = build_dataset([_row("g1"), _row("g2")], use_move=True)
    assert x.shape == (2, n_planes(True), 8, 8)
    assert y.shape == (2,)
    assert themes.shape == (2, len(THEME_VOCAB))
    assert game_ids == ["g1", "g2"]


def test_build_dataset_without_move_has_fewer_planes() -> None:
    x, _, _, _ = build_dataset([_row("g1")], use_move=False)
    assert x.shape[1] == n_planes(False)


def test_build_dataset_rejects_empty() -> None:
    with pytest.raises(ValueError):
        build_dataset([])


def test_group_split_keeps_games_whole_and_disjoint() -> None:
    game_ids = [f"g{i}" for i in range(10) for _ in range(5)]
    split = group_split(game_ids, seed=7)
    groups = {name: {game_ids[i] for i in idx} for name, idx in split.items()}
    assert not (groups["train"] & groups["val"])
    assert not (groups["train"] & groups["test"])
    assert not (groups["val"] & groups["test"])
    assert groups["test"]  # at least one game reaches the held-out split
    assert sum(len(idx) for idx in split.values()) == len(game_ids)
