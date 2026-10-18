"""The Lichess tag vocabulary and its mapping onto our theme vocab.

The mapping is the contract between the independent ground truth (puzzle tags) and our
labels, so it is pinned in both directions: every mapped theme must exist in
``THEME_VOCAB`` (or the benchmark would benchmark against a name no detector can emit), and
the mapping must be injective (or the inverse is ambiguous).
"""

from __future__ import annotations

from moveexp.config import THEME_VOCAB
from moveexp.data import puzzle_themes as pt


def test_every_mapped_theme_is_in_the_vocabulary():
    unknown = set(pt.PUZZLE_TAG_TO_THEME.values()) - set(THEME_VOCAB)
    assert not unknown, f"mapped themes not in THEME_VOCAB: {sorted(unknown)}"


def test_mapping_is_injective():
    values = list(pt.PUZZLE_TAG_TO_THEME.values())
    assert len(values) == len(set(values))


def test_theme_to_tags_is_the_inverse():
    for tag, theme in pt.PUZZLE_TAG_TO_THEME.items():
        assert tag in pt.THEME_TO_TAGS[theme]


def test_mapped_tags_are_known_lichess_tags():
    assert set(pt.PUZZLE_TAG_TO_THEME) <= set(pt.LICHESS_THEMES)


def test_themes_from_tags_maps_ignores_and_orders():
    themes = pt.themes_from_tags(["sacrifice", "fork", "crushing", "opening", "madeUpTag"])
    assert set(themes) == {"fork", "sacrifice"}
    # Result is in THEME_VOCAB order, so it is deterministic across runs.
    assert themes == [t for t in THEME_VOCAB if t in {"fork", "sacrifice"}]


def test_themes_from_tags_drops_non_tactic_tags_entirely():
    assert pt.themes_from_tags(["opening", "endgame", "short", "crushing", "master"]) == []


def test_the_tactic_tags_the_detectors_cover_are_mapped():
    # Every tag the new detectors target must have a mapping, or its detector could never be
    # measured by the benchmark.
    for tag in (
        "fork",
        "pin",
        "skewer",
        "discoveredAttack",
        "doubleCheck",
        "hangingPiece",
        "trappedPiece",
        "deflection",
        "interference",
        "xRayAttack",
        "overloading",
        "attraction",
        "clearance",
        "capturingDefender",
        "intermezzo",
        "quietMove",
        "zugzwang",
        "smotheredMate",
        "backRankMate",
        "enPassant",
        "underPromotion",
        "advancedPawn",
        "attackingF2F7",
        "kingsideAttack",
        "queensideAttack",
        "defensiveMove",
    ):
        assert tag in pt.PUZZLE_TAG_TO_THEME, tag
