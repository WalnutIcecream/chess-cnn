"""The Lichess puzzle tag vocabulary and its mapping onto :data:`moveexp.config.THEME_VOCAB`.

Lichess tags every puzzle automatically and then refines the tags with player votes, which
makes them an *independent* label: they were not produced by this project's detectors. That
is what turns :mod:`eval.puzzle_benchmark` into a real measurement instead of a tautology.

A Lichess puzzle carries several kinds of tag at once:

* **tactics** -- board-verifiable motifs (``fork``, ``pin``, ``attraction``, ...). These are
  what a detector can be measured against, so only these are mapped.
* **mate** -- ``mateIn2``, ``smotheredMate``, ... (a subset overlaps the tactics).
* **phase / length / strength** -- ``opening``, ``endgame``, ``short``, ``crushing``, ``master``.
  These are properties of the game, not of the move, so they are dropped.

:data:`PUZZLE_TAG_TO_THEME` is the bridge used by both the benchmark and the concept-dataset
builder, so both measure the same label space (the theme vocabulary).
"""

from __future__ import annotations

from collections.abc import Iterable

from ..config import THEME_VOCAB

__all__ = [
    "LENGTH_TAGS",
    "LICHESS_THEMES",
    "MATE_TAGS",
    "MOVE_LEVEL_TAGS",
    "MOVE_LEVEL_THEMES",
    "PHASE_TAGS",
    "PUZZLE_LEVEL_TAGS",
    "PUZZLE_LEVEL_THEMES",
    "PUZZLE_TAG_TO_THEME",
    "STRENGTH_TAGS",
    "TACTIC_TAGS",
    "THEME_TO_TAGS",
    "tag_group",
    "theme_group",
    "themes_from_tags",
]

#: Tactic tags that name a board-verifiable motif. This is the measurable subset.
TACTIC_TAGS: tuple[str, ...] = (
    "advancedPawn",
    "attackingF2F7",
    "attraction",
    "capturingDefender",
    "clearance",
    "defensiveMove",
    "deflection",
    "discoveredAttack",
    "doubleCheck",
    "enPassant",
    "fork",
    "hangingPiece",
    "interference",
    "intermezzo",
    "kingsideAttack",
    "overloading",
    "pin",
    "promotion",
    "queensideAttack",
    "quietMove",
    "sacrifice",
    "skewer",
    "trappedPiece",
    "underPromotion",
    "xRayAttack",
    "zugzwang",
)

#: Mate tags. Only the named patterns with a distinct shape are mapped; ``mateIn2`` etc.
#: merely restate that the puzzle ends in mate and are not a motif.
MATE_TAGS: tuple[str, ...] = (
    "mate",
    "mateIn1",
    "mateIn2",
    "mateIn3",
    "mateIn4",
    "mateIn5",
    "anastasiaMate",
    "arabianMate",
    "backRankMate",
    "bodenMate",
    "doubleBishopMate",
    "dovetailMate",
    "hookMate",
    "smotheredMate",
    "damianoMate",
    "greekGiftMate",
    "killBoxMate",
    "vukovicMate",
    "epauletteMate",
    "swallowtailMate",
)

#: Tags that describe the phase of the game, not the move.
PHASE_TAGS: tuple[str, ...] = ("opening", "middlegame", "endgame")

#: Puzzles are bucketed by how many moves the solution takes.
LENGTH_TAGS: tuple[str, ...] = ("oneMove", "short", "long", "veryLong")

#: Tags that describe how decisive the position is, or who played it. Not move properties.
STRENGTH_TAGS: tuple[str, ...] = (
    "advantage",
    "crushing",
    "equality",
    "master",
    "masterVsMaster",
    "superGM",
)

#: Every Lichess puzzle tag this project knows about (the union of the groups above plus the
#: endgame-material tags). Used to sanity-check the mapping in tests; Lichess may add tags, so
#: :func:`themes_from_tags` tolerates unknown ones.
LICHESS_THEMES: tuple[str, ...] = (
    *TACTIC_TAGS,
    *MATE_TAGS,
    *PHASE_TAGS,
    *LENGTH_TAGS,
    *STRENGTH_TAGS,
    "bishopEndgame",
    "knightEndgame",
    "pawnEndgame",
    "queenEndgame",
    "queenRookEndgame",
    "rookEndgame",
    "bishopPawnEndgame",
    "knightPawnEndgame",
    "queenPawnEndgame",
    "rookPawnEndgame",
    "exposedKing",
)

#: The bridge: Lichess tag -> a name in :data:`moveexp.config.THEME_VOCAB`. Append-only, and
#: injective (no two tags share a theme) so the inverse is well defined.
PUZZLE_TAG_TO_THEME: dict[str, str] = {
    "advancedPawn": "advanced_pawn",
    "attackingF2F7": "attacking_f2f7",
    "attraction": "attraction",
    "backRankMate": "back_rank_mate",
    "capturingDefender": "capturing_defender",
    "clearance": "clearance",
    "defensiveMove": "defensive_move",
    "deflection": "deflection",
    "discoveredAttack": "discovered_attack",
    "doubleCheck": "double_check",
    "enPassant": "en_passant",
    "fork": "fork",
    "hangingPiece": "hanging_piece",
    "interference": "interference",
    "intermezzo": "intermezzo",
    "kingsideAttack": "kingside_attack",
    "overloading": "overloaded_defender",
    "pin": "pin",
    "promotion": "promotion",
    "queensideAttack": "queenside_attack",
    "quietMove": "quiet_move",
    "sacrifice": "sacrifice",
    "skewer": "skewer",
    "smotheredMate": "smothered_mate",
    "trappedPiece": "trapped_piece",
    "underPromotion": "under_promotion",
    "xRayAttack": "x_ray",
    "zugzwang": "zugzwang",
}

#: Inverse of :data:`PUZZLE_TAG_TO_THEME`: theme -> the tags that imply it.
THEME_TO_TAGS: dict[str, tuple[str, ...]] = {
    theme: tuple(tag for tag, mapped in PUZZLE_TAG_TO_THEME.items() if mapped == theme)
    for theme in dict.fromkeys(PUZZLE_TAG_TO_THEME.values())
}


def themes_from_tags(tags: Iterable[str]) -> list[str]:
    """Map Lichess tags to theme-vocab names, de-duplicated and in vocabulary order.

    Unknown tags (Lichess adds new ones over time) and non-tactic tags are ignored rather
    than raising, so a corpus change can never break a run.
    """
    wanted = {PUZZLE_TAG_TO_THEME[tag] for tag in tags if tag in PUZZLE_TAG_TO_THEME}
    return [theme for theme in THEME_VOCAB if theme in wanted]


# --------------------------------------------------------------------------------------
# Tag groups: what a per-move detector can and cannot be held to
# --------------------------------------------------------------------------------------
# The measured benchmark (PROGRESS §19) splits cleanly along this line, so it is made
# explicit here instead of being rediscovered in every discussion of the numbers.

#: Tags whose truth is a property of a single position and its move -- "this move forks",
#: "this move promotes". A per-move rule can, in principle, decide these exactly, and the
#: detectors score F1 0.5-1.0 on them.
MOVE_LEVEL_TAGS: tuple[str, ...] = (
    "advancedPawn",
    "attackingF2F7",
    "backRankMate",
    "deflection",
    "discoveredAttack",
    "doubleCheck",
    "enPassant",
    "fork",
    "hangingPiece",
    "interference",
    "overloading",
    "pin",
    "promotion",
    "sacrifice",
    "skewer",
    "smotheredMate",
    "trappedPiece",
    "underPromotion",
    "xRayAttack",
)

#: Tags that describe the *puzzle*, not the move -- "this is a kingside attack", "the point is
#: a quiet move", "the opponent is in zugzwang". They hold of the whole solution, so a
#: per-move rule is structurally mismatched to them however it is tuned. They are kept in the
#: label space and reported separately rather than deleted, so the measurement says so out
#: loud instead of the aggregate quietly being dragged down by them.
PUZZLE_LEVEL_TAGS: tuple[str, ...] = (
    "attraction",
    "capturingDefender",
    "clearance",
    "defensiveMove",
    "intermezzo",
    "kingsideAttack",
    "queensideAttack",
    "quietMove",
    "zugzwang",
)

_TAG_GROUP: dict[str, str] = {
    **{tag: "move" for tag in MOVE_LEVEL_TAGS},
    **{tag: "puzzle" for tag in PUZZLE_LEVEL_TAGS},
}

#: Themes (what the benchmark compares) in each group, derived from the tag groups.
MOVE_LEVEL_THEMES: frozenset[str] = frozenset(PUZZLE_TAG_TO_THEME[tag] for tag in MOVE_LEVEL_TAGS)
PUZZLE_LEVEL_THEMES: frozenset[str] = frozenset(
    PUZZLE_TAG_TO_THEME[tag] for tag in PUZZLE_LEVEL_TAGS
)


def tag_group(tag: str) -> str | None:
    """``"move"`` or ``"puzzle"`` for a mapped Lichess tag; ``None`` if it is not mapped."""
    return _TAG_GROUP.get(tag)


def theme_group(theme: str) -> str | None:
    """``"move"`` or ``"puzzle"`` for a theme the mapping covers; ``None`` otherwise."""
    if theme in MOVE_LEVEL_THEMES:
        return "move"
    if theme in PUZZLE_LEVEL_THEMES:
        return "puzzle"
    return None
