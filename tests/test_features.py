"""Tests for :mod:`moveexp.analysis.features`.

The feature counts are simple, which makes them easy to get quietly wrong in three ways:
asking python-chess the opposite question (``attacks_mask`` instead of ``attackers_mask``),
counting a side's own pieces as its mobility, and writing a structural term -- "backward
pawn", "outpost" -- that is constant in a real position and therefore carries no signal.
The tests below pin all three down, and every expected number is derived from the count
definition rather than copied from the implementation.
"""

from __future__ import annotations

import chess
import pytest

from moveexp.analysis.features import (
    FEATURE_GROUPS,
    FeatureSnapshot,
    centre_distance,
    is_outpost,
    king_zone,
    positional_delta,
    snapshot,
)
from moveexp.config import (
    BACKWARD_PAWN_CP,
    DOUBLED_PAWN_CP,
    FEATURE_WEIGHTS,
    ISOLATED_PAWN_CP,
    KING_ATTACK_WEIGHT,
    PASSED_PAWN_BONUS_CP,
    PIECE_CENTRALITY,
    PIECE_VALUE_CP,
)
from moveexp.schema import PositionalDelta
from positions import after, board

KINGS = ("wK@e1", "bK@e8")


# ------------------------------------------------------------------ shape of the module
def test_feature_groups_match_the_config_weights_and_the_schema():
    assert tuple(FEATURE_WEIGHTS) == FEATURE_GROUPS
    assert set(FEATURE_GROUPS) <= set(PositionalDelta.model_fields)


def test_snapshot_is_immutable():
    snap = snapshot(chess.Board(), chess.WHITE)
    with pytest.raises(AttributeError):
        snap.mobility = 1.0


def test_positional_delta_rejects_illegal_moves():
    b = chess.Board()
    with pytest.raises(ValueError, match="not legal"):
        positional_delta(b, chess.Move.from_uci("e2e5"))


# ------------------------------------------------------------------- starting position
def test_starting_position_is_symmetric_and_has_no_structural_faults():
    """Both sides see the same numbers, and the opening is not "eight backward pawns"."""
    white = snapshot(chess.Board(), chess.WHITE)
    black = snapshot(chess.Board(), chess.BLACK)

    assert white.as_tuple() == black.as_tuple()
    assert white.material_cp == 0.0
    assert white.pawn_structure == 0.0
    assert white.space == 0.0
    # 3 shield pawns in front of the king and no enemy pressure yet.
    assert white.king_safety == 3.0


# ------------------------------------------------------------------------- geometry
@pytest.mark.parametrize(
    ("name", "expected"),
    [("d4", 0), ("e4", 0), ("d5", 0), ("e5", 0), ("c3", 1), ("b2", 2), ("a1", 3), ("h8", 3)],
)
def test_centre_distance(name: str, expected: int):
    assert centre_distance(chess.parse_square(name)) == expected


def test_king_zone_is_three_files_wide_and_clamped_at_the_edges():
    b = board("wK@e1", "bK@e8")
    assert len(king_zone(b, chess.WHITE)) == 9
    assert len(king_zone(b, chess.BLACK)) == 9

    corner = board("wK@a1", "bK@h8")
    zone = king_zone(corner, chess.WHITE)
    assert len(zone) == 6  # files a-b, ranks 1-3
    assert chess.A1 in zone and chess.B3 in zone and chess.C1 not in zone


def test_king_zone_of_a_side_without_a_king_is_empty():
    kingless = chess.Board("8/8/8/8/8/8/8/4K3 w - - 0 1")
    assert len(king_zone(kingless, chess.BLACK)) == 0


# ------------------------------------------------------------------------- material
def test_capture_shows_up_as_material():
    b = board("wN@c3", "bN@d5", *KINGS)
    delta = positional_delta(b, b.parse_san("Nxd5"))

    assert delta.material == pytest.approx(PIECE_VALUE_CP["n"])


# ------------------------------------------------------------------- pawn structure
def test_doubled_pawns_are_penalised():
    """Two pawns on the a-file: one doubled penalty, both isolated, both passed."""
    b = board(*KINGS, "wP@a2", "wP@a4")
    assert snapshot(b, chess.WHITE).pawn_structure == pytest.approx(
        -DOUBLED_PAWN_CP - 2 * ISOLATED_PAWN_CP + 2 * PASSED_PAWN_BONUS_CP
    )


def test_isolated_pawn_is_penalised_but_a_passed_one_pays_for_it():
    b = board(*KINGS, "wP@a2")
    assert snapshot(b, chess.WHITE).pawn_structure == pytest.approx(
        -ISOLATED_PAWN_CP + PASSED_PAWN_BONUS_CP
    )


def test_backward_pawn_needs_to_be_stuck_and_unsupported():
    """a4: the b2 pawn cannot defend it and b6 controls a5, so a4 can do nothing."""
    backward = board(*KINGS, "wP@a4", "wP@b2", "bP@b6")
    assert snapshot(backward, chess.WHITE).pawn_structure == pytest.approx(-BACKWARD_PAWN_CP)

    # Same pawn, but with support on b4: no longer backward.
    supported = board(*KINGS, "wP@a4", "wP@b4", "bP@b6")
    assert snapshot(supported, chess.WHITE).pawn_structure >= 0.0


def test_blocked_pawn_is_not_backward():
    """A pawn facing an enemy pawn (e4 vs e5) is blocked, not backward.

    The d2 pawn gives e4 a neighbour so it is not isolated; the point is that the *blocked*
    e4 pawn must not also be counted as backward.
    """
    blocked = board(*KINGS, "wP@e4", "bP@e5", "wP@d2")
    assert snapshot(blocked, chess.WHITE).pawn_structure == 0.0


def test_developed_pawn_is_not_backward():
    """A pawn that can still advance is undeveloped, not backward.

    Same shape as the backward case above, but the blocking pawn is on a7 instead of b6, so
    a4 has no enemy pawn waiting on a5 -- and the term drops back to zero. Without this the
    feature would be a constant in every real position.
    """
    developed = board(*KINGS, "wP@a4", "wP@b2", "bP@a7")
    assert snapshot(developed, chess.WHITE).pawn_structure == 0.0


def test_pawn_structure_is_symmetric_across_colours():
    b = board("wK@e1", "bK@e8", "wP@a4", "bP@a5", "wP@d2", "bP@d7")
    assert snapshot(b, chess.WHITE).pawn_structure == pytest.approx(
        snapshot(b, chess.BLACK).pawn_structure
    )


# ------------------------------------------------------------------------- outposts
def test_outpost_needs_advance_pawn_defence_and_pawn_safety():
    good = board(*KINGS, "wN@c5", "wP@b4")
    assert is_outpost(good, chess.parse_square("c5"))

    # A knight on f3 is defended by g2 and untouchable by a pawn, but it is nowhere near the
    # fight: no outpost.
    home = board(*KINGS, "wN@f3", "wP@g2")
    assert not is_outpost(home, chess.parse_square("f3"))

    undefended = board(*KINGS, "wN@c5")
    assert not is_outpost(undefended, chess.parse_square("c5"))

    beatable = board(*KINGS, "wN@c5", "wP@b4", "bP@b6")
    assert not is_outpost(beatable, chess.parse_square("c5"))

    # Rooks and queens are never outposts.
    rook = board(*KINGS, "wR@c5", "wP@b4")
    assert not is_outpost(rook, chess.parse_square("c5"))
    assert not is_outpost(good, chess.parse_square("b4"))  # a pawn there


def test_outpost_rule_is_colour_symmetric():
    """The same shape for Black: a knight on e4 guarded by the d5 pawn is an outpost too."""
    b = board(*KINGS, "bN@e4", "bP@d5")
    assert is_outpost(b, chess.parse_square("e4"))


# ---------------------------------------------------------------------- activity terms
def test_activity_rewards_a_piece_in_the_centre():
    start = chess.Board()
    delta = positional_delta(start, start.parse_san("Nf3"))
    g1 = chess.parse_square("g1")
    f3 = chess.parse_square("f3")

    expected = (
        PIECE_CENTRALITY["n"][centre_distance(f3)] - PIECE_CENTRALITY["n"][centre_distance(g1)]
    )
    assert delta.activity == pytest.approx(expected * FEATURE_WEIGHTS["activity"])


# ----------------------------------------------------------------------- king safety
def test_moving_a_shield_pawn_costs_king_safety():
    start = chess.Board()
    delta = positional_delta(start, start.parse_san("e4"))

    assert delta.king_safety == pytest.approx(-FEATURE_WEIGHTS["king_safety"])


def test_the_enemy_king_counts_less_than_a_rook():
    """Attacking the same zone with the king instead of a rook is worth less.

    White's king on e1 covers files d-f, ranks 1-3. A black rook on d4 hits d1, d2 and d3 (three
    squares, ``-3``); a black king on d4 only reaches d3 and e3, so it counts
    ``2 x KING_ATTACK_WEIGHT``. Same zone, same attacker square, different weight.
    """
    rook = board("wK@e1", "bR@d4", "bK@a8")
    king = board("wK@e1", "bK@d4")

    assert snapshot(rook, chess.WHITE).king_safety == pytest.approx(-3.0)
    assert snapshot(king, chess.WHITE).king_safety == pytest.approx(-2 * KING_ATTACK_WEIGHT)


def test_castling_improves_the_king_zone():
    b = after("e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5", "d3", "g6")
    delta = positional_delta(b, b.parse_san("O-O"))

    assert delta.king_safety > 0.0


# ------------------------------------------------------------------------- mobility
def test_mobility_counts_destinations_not_own_pieces():
    """Ra1 reaches b1-d1 and a2-a8 (ten squares); its own pawn on a2 takes seven of them away.

    A piece "defending" its own pawn is not mobility, and counting it would make a blocked
    rook look more active than a free one.
    """
    free = board(*KINGS, "wR@a1")
    blocked = board(*KINGS, "wR@a1", "wP@a2")

    assert snapshot(free, chess.WHITE).mobility == 10.0
    assert snapshot(blocked, chess.WHITE).mobility == 3.0


def test_pawns_and_king_do_not_count_as_mobility():
    b = board(*KINGS, "wP@e4")
    assert snapshot(b, chess.WHITE).mobility == 0.0


# --------------------------------------------------------------------------- perspective
def test_delta_is_from_the_mover_point_of_view_for_both_colours():
    """The same shape of move helps whoever plays it."""
    white_to_move = after("e4", "e5", "Nf3", "Nc6")
    black_to_move = after("e4", "e5", "Nf3")

    white_develop = positional_delta(white_to_move, white_to_move.parse_san("Bc4"))
    black_develop = positional_delta(black_to_move, black_to_move.parse_san("Nc6"))

    assert white_develop.activity > 0.0
    assert black_develop.activity > 0.0
    assert white_develop.space >= 0.0
    assert black_develop.space >= 0.0


# --------------------------------------------------------------------- weighting layer
def test_delta_vector_is_the_weighted_difference():
    b = after("e4", "e5", "Nf3", "Nc6", "Bc4")
    before = snapshot(after("e4"), chess.WHITE)
    after_snap = snapshot(b, chess.WHITE)

    raw = tuple(
        after_value - start
        for after_value, start in zip(after_snap.as_tuple(), before.as_tuple(), strict=True)
    )
    expected = tuple(
        value * FEATURE_WEIGHTS[group] for group, value in zip(FEATURE_GROUPS, raw, strict=True)
    )

    assert after_snap.delta_vector(before) == pytest.approx(expected)


def test_delta_from_matches_the_schema():
    b = after("e4", "e5", "Nf3", "Nc6")
    before = snapshot(b, chess.WHITE)
    after_snap = snapshot(after("e4", "e5", "Nf3"), chess.WHITE)

    delta = after_snap.delta_from(before)
    assert isinstance(delta, PositionalDelta)
    for group in FEATURE_GROUPS:
        assert getattr(delta, group) == pytest.approx(
            after_snap.delta_vector(before)[FEATURE_GROUPS.index(group)]
        )


def test_snapshot_reports_its_own_side():
    b = board(*KINGS, "wQ@d1", "bR@a8")
    assert snapshot(b, chess.WHITE).side is chess.WHITE
    assert snapshot(b, chess.WHITE).material_cp == pytest.approx(
        PIECE_VALUE_CP["q"] - PIECE_VALUE_CP["r"]
    )
    assert snapshot(b, chess.BLACK).material_cp == pytest.approx(
        PIECE_VALUE_CP["r"] - PIECE_VALUE_CP["q"]
    )


def test_feature_snapshot_can_be_built_directly():
    """Detectors may want to report a partial picture without counting anything."""
    manual = FeatureSnapshot(
        chess.WHITE,
        material_cp=0.0,
        mobility=1.0,
        king_safety=0.0,
        pawn_structure=0.0,
        space=0.0,
        activity=0.0,
    )
    assert manual.weighted() == (0.0, FEATURE_WEIGHTS["mobility"], 0.0, 0.0, 0.0, 0.0)
