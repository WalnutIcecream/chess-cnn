#!/usr/bin/env python3
"""Build the small, committed puzzle fixture the offline tests run against.

The real corpus is a 300 MB download and git-ignored, so anything that needs to *measure* the
detectors needs a small stand-in. A plain random sample will not do: the rare motifs
(``enPassant``, ``smotheredMate``, ``xRayAttack``) would turn up a handful of times and their
precision/recall would be noise. The fixture is therefore **stratified** -- up to
``--per-theme`` puzzles for every mapped theme -- so every theme stays measurable while the
file stays around a hundred KB.

Deterministic: per-theme reservoir sampling with a fixed seed, so rerunning reproduces the
same file byte for byte.

Run inside the venv::

    python scripts/make_puzzle_fixture.py                       # -> tests/data/puzzles_sample.csv
    python scripts/make_puzzle_fixture.py --per-theme 30
"""

from __future__ import annotations

import argparse
import csv
import random
from collections.abc import Iterable
from pathlib import Path

from moveexp.config import DEFAULT_SEED, PROJECT_ROOT, RAW_DIR
from moveexp.data.lichess import PUZZLE_COLUMNS, Puzzle, format_puzzle_row, stream_puzzles
from moveexp.data.puzzle_themes import PUZZLE_TAG_TO_THEME, themes_from_tags

PUZZLE_RAW = RAW_DIR / "lichess_db_puzzle.csv.zst"
FIXTURE = PROJECT_ROOT / "tests" / "data" / "puzzles_sample.csv"


def stratified_sample(
    puzzles: Iterable[Puzzle], *, per_theme: int = 20, seed: int = DEFAULT_SEED
) -> list[Puzzle]:
    """Keep up to ``per_theme`` puzzles for every mapped theme (one reservoir per theme).

    Puzzles are returned sorted by id, so the file is stable even though the sampling streams.
    """
    buckets: dict[str, list[Puzzle]] = {theme: [] for theme in set(PUZZLE_TAG_TO_THEME.values())}
    seen: dict[str, int] = dict.fromkeys(buckets, 0)
    rng = random.Random(seed)

    for puzzle in puzzles:
        for theme in themes_from_tags(puzzle.themes):
            seen[theme] += 1
            bucket = buckets[theme]
            if len(bucket) < per_theme:
                bucket.append(puzzle)
            else:
                slot = rng.randint(0, seen[theme] - 1)
                if slot < per_theme:
                    bucket[slot] = puzzle

    unique: dict[str, Puzzle] = {}
    for theme in sorted(buckets):
        for puzzle in buckets[theme]:
            unique.setdefault(puzzle.puzzle_id, puzzle)
    return [unique[pid] for pid in sorted(unique)]


def _write(puzzles: list[Puzzle], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(PUZZLE_COLUMNS)
        writer.writerows(format_puzzle_row(puzzle) for puzzle in puzzles)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--puzzles", type=Path, default=PUZZLE_RAW, help="Puzzle CSV (.zst ok).")
    parser.add_argument("--per-theme", type=int, default=20, help="Puzzles kept per theme.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--out", type=Path, default=FIXTURE)
    args = parser.parse_args(argv)

    if not args.puzzles.exists():
        raise SystemExit(f"{args.puzzles} not found; run scripts/download_data.py puzzles first")

    sample = stratified_sample(
        stream_puzzles(args.puzzles), per_theme=args.per_theme, seed=args.seed
    )
    _write(sample, args.out)

    counts: dict[str, int] = {theme: 0 for theme in set(PUZZLE_TAG_TO_THEME.values())}
    for puzzle in sample:
        for theme in themes_from_tags(puzzle.themes):
            counts[theme] += 1
    covered = sum(1 for count in counts.values() if count)
    print(f"wrote {len(sample)} puzzles ({args.out.stat().st_size / 1024:.0f} KiB) to {args.out}")
    print(f"themes covered: {covered}/{len(counts)}")
    missing = sorted(theme for theme, count in counts.items() if not count)
    if missing:
        print(f"  no puzzle found for: {', '.join(missing)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
