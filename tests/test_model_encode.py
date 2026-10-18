"""Tests for the neural baseline's encoder and dataset helpers (no torch required)."""

from __future__ import annotations

import numpy as np
import pytest

from moveexp.config import THEME_VOCAB
from moveexp.model import (
    N_PLANES,
    augment_planes,
    build_dataset,
    colour_flip,
    encode_board,
    group_split,
    mirror_files,
    n_planes,
)
from moveexp.model.encode import PIECE_PLANES

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


# ------------------------------------------------------------------ symmetry augmentation
def test_mirror_files_sends_the_a_file_to_the_h_file() -> None:
    x = encode_board("8/8/8/8/8/8/8/N7 w - - 0 1")  # a lone white knight on a1
    mirrored = mirror_files(x)
    assert mirrored[PIECE_PLANES.index("N"), 7, 7] == 1.0  # a1 -> h1
    assert mirrored[:12].sum() == 1.0
    assert mirrored[12].sum() == 64.0  # side to move is unchanged by a reflection


def test_colour_flip_swaps_colours_and_rotates() -> None:
    x = encode_board("8/8/8/8/8/8/4P3/8 w - - 0 1")  # a lone white pawn on e2
    flipped = colour_flip(x)
    # e2 -> colour-swapped and rotated 180 degrees -> black pawn on d7 (row 1, file 3).
    assert flipped[PIECE_PLANES.index("p"), 1, 3] == 1.0
    assert flipped[:12].sum() == 1.0
    assert flipped[12].sum() == 0.0  # now black to move


def test_colour_flip_is_an_involution() -> None:
    x = encode_board(START_FEN, "e2e4")
    assert np.array_equal(colour_flip(colour_flip(x)), x)


def test_augment_planes_defaults_to_identity() -> None:
    x = encode_board(START_FEN, "e2e4")
    assert np.array_equal(augment_planes(x), x)


def test_augment_planes_works_on_a_whole_batch() -> None:
    batch = np.stack([encode_board(START_FEN), encode_board(BLACK_FEN)])
    out = augment_planes(batch, mirror=True, switch_colour=True)
    assert out.shape == batch.shape
    assert out[..., :12, :, :].sum() == batch[..., :12, :, :].sum()  # pieces are conserved
