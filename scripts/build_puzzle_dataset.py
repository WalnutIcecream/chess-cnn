#!/usr/bin/env python3
"""Build a labelled concept dataset from the Lichess puzzle export.

One row per **solver move**: the position the solver faces (`fen_before`), the move the puzzle
considers correct (`move_uci`), and the puzzle's tactic tags mapped onto ``THEME_VOCAB``
(`theme_vector`). The tags are Lichess's -- automatically generated and then refined by player
votes -- so they are *independent* of this project's detectors. That is the whole point: the
concept classifier is trained, and the detectors are measured, against ground truth we did not
produce.

By default only the puzzle's key move (the first solver move) is emitted, which gives a clean
one-position-one-motif target. ``--all-solver-moves`` emits every solver move in the solution
at the cost of noisier labels (a long puzzle's tags need not apply to each of its moves).

Rows are deduplicated by **normalised FEN** (``--dedupe``, on by default): many puzzles share a
position, and a repeated position both inflates the dataset and can leak across the train/test
split. Each row also records its ``rating_band`` and the ``tag_groups`` (move-level / puzzle-
level) its themes belong to, so the build summary can show the sample's composition.

Run inside the venv::

    python scripts/build_puzzle_dataset.py --n 200000
    python scripts/train_concepts.py --labels data/processed/puzzles.parquet
"""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import pandas as pd

from moveexp.config import DEFAULT_SEED, PROCESSED_DIR, RAW_DIR, THEME_VOCAB
from moveexp.data.lichess import Puzzle, reservoir_sample, stream_puzzles
from moveexp.data.puzzle_themes import (
    MOVE_LEVEL_THEMES,
    PUZZLE_LEVEL_THEMES,
    theme_group,
    themes_from_tags,
)
from moveexp.schema import normalise_fen, theme_multi_hot

PUZZLE_RAW = RAW_DIR / "lichess_db_puzzle.csv.zst"
PUZZLE_PARQUET = PROCESSED_DIR / "puzzles.parquet"

#: Rating bucket boundaries for the summary and the ``rating_band`` column. Puzzles run from
#: roughly 400 to 3000, so these split that range into readable bands.
RATING_BANDS: tuple[int, ...] = (1200, 1600, 2000, 2400)


def rating_band(rating: int) -> str:
    """Bucket a puzzle rating, e.g. ``1199 -> "<1200"``, ``1600 -> "1600-1999"``."""
    lower: int | None = None
    for bound in RATING_BANDS:
        if rating < bound:
            return f"<{bound}" if lower is None else f"{lower}-{bound - 1}"
        lower = bound
    return f"{RATING_BANDS[-1]}+"


def tag_groups(theme_names: Iterable[str]) -> str:
    """The tag groups a row's themes belong to: ``"move"``, ``"puzzle"`` or ``"move puzzle"``."""
    groups = sorted({group for name in theme_names if (group := theme_group(name))})
    return " ".join(groups)


def dedupe_by_position(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep the first row for each position, preserving input order.

    Position identity is the project's normalised FEN -- board, side, castling and en-passant
    only, counters dropped (``moveexp.schema``) -- so two rows that differ solely in the move
    clock are treated as the same position.
    """
    seen: set[str] = set()
    kept: list[dict[str, Any]] = []
    for row in rows:
        key = normalise_fen(row["fen_before"])
        if key in seen:
            continue
        seen.add(key)
        kept.append(row)
    return kept


def rows_from_puzzles(
    puzzles: list[Puzzle], *, all_solver_moves: bool = False
) -> list[dict[str, Any]]:
    """Flatten puzzles into labelled rows (one per solver move, the key move by default)."""
    rows: list[dict[str, Any]] = []
    for puzzle in puzzles:
        targets = themes_from_tags(puzzle.themes)
        if not targets:
            continue  # no mapped tactic: the row would have an all-zero target
        try:
            board = puzzle.position_after_blunder()
        except ValueError:
            continue  # the recorded blunder is not legal in the FEN: skip rather than crash
        vector = theme_multi_hot(targets)
        for index, move in enumerate(puzzle.solution_moves()):
            if move not in board.legal_moves:
                break
            if index % 2 == 0:  # the solver moves on even indices of the solution line
                rows.append(
                    {
                        "puzzle_id": puzzle.puzzle_id,
                        "ply": index,
                        "fen_before": board.fen(),
                        "move_uci": move.uci(),
                        "rating": puzzle.rating,
                        "rating_band": rating_band(puzzle.rating),
                        "tag_groups": tag_groups(targets),
                        "themes": " ".join(targets),
                        "puzzle_tags": " ".join(puzzle.themes),
                        "theme_vector": vector,
                        "source": "puzzle",
                        "label_source": "puzzle_tag",
                    }
                )
                if not all_solver_moves:
                    break
            board.push(move)
    return rows


def _prevalence(rows: list[dict[str, Any]]) -> Counter:
    """How often each theme occurs, for the build summary."""
    counts: Counter = Counter()
    for row in rows:
        for theme, flag in zip(THEME_VOCAB, row["theme_vector"], strict=True):
            if flag:
                counts[theme] += 1
    return counts


def _print_summary(rows: list[dict[str, Any]], *, sampled: int, dropped: int, out: Path) -> None:
    """Report what the build actually produced: size, coverage, and sample composition."""
    counts = _prevalence(rows)
    move_themes = sorted(set(counts) & MOVE_LEVEL_THEMES)
    puzzle_themes = sorted(set(counts) & PUZZLE_LEVEL_THEMES)
    by_group = Counter(str(row["tag_groups"]) for row in rows)
    by_band = Counter(str(row["rating_band"]) for row in rows)

    print(f"wrote {len(rows)} rows to {out}")
    print(f"  sampled {sampled} puzzles; {dropped} rows dropped as duplicate positions")
    print(
        f"  themes covered: {len(counts)} of {len(THEME_VOCAB)} "
        f"(move-level {len(move_themes)}, puzzle-level {len(puzzle_themes)})"
    )
    print("  rows by tag group:")
    for group, count in sorted(by_group.items(), key=lambda item: -item[1]):
        print(f"    {group:<14} {count:>8}  ({count / len(rows):.1%})")
    print("  rows by rating band:")
    for band in sorted(by_band, key=_band_order):
        count = by_band[band]
        print(f"    {band:<14} {count:>8}  ({count / len(rows):.1%})")
    print("  most common tags:")
    for theme, count in counts.most_common(8):
        print(f"    {theme:<22} {count:>8}  ({count / len(rows):.1%})")


def _band_order(band: str) -> tuple[int, int]:
    """Order rating bands low to high, since they sort as text otherwise."""
    if band.endswith("+"):
        return (len(RATING_BANDS), 0)
    if band.startswith("<"):
        return (0, 0)
    lower = int(band.split("-")[0])
    return (RATING_BANDS.index(lower) + 1, lower)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--puzzles", type=Path, default=PUZZLE_RAW, help="Puzzle CSV (.zst ok).")
    parser.add_argument("--n", type=int, default=200_000, help="How many puzzles to sample.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--out", type=Path, default=PUZZLE_PARQUET)
    parser.add_argument(
        "--all-solver-moves",
        action="store_true",
        help="Emit every solver move instead of only the puzzle's key move (noisier labels).",
    )
    parser.add_argument(
        "--dedupe",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Drop repeated positions (normalised FEN), keeping the first row for each.",
    )
    args = parser.parse_args(argv)

    if not args.puzzles.exists():
        raise SystemExit(f"{args.puzzles} not found; run scripts/download_data.py puzzles first")

    puzzles = reservoir_sample(stream_puzzles(args.puzzles), args.n, seed=args.seed)
    print(f"sampled {len(puzzles)} puzzles")
    rows = rows_from_puzzles(puzzles, all_solver_moves=args.all_solver_moves)
    if not rows:
        raise SystemExit("no usable rows; is this a puzzle CSV?")

    dropped = 0
    if args.dedupe:
        before = len(rows)
        rows = dedupe_by_position(rows)
        dropped = before - len(rows)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(args.out, engine="pyarrow", index=False)

    _print_summary(rows, sampled=len(puzzles), dropped=dropped, out=args.out)
    print(f"next: python scripts/train_concepts.py --labels {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
