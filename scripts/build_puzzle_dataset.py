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

Run inside the venv::

    python scripts/build_puzzle_dataset.py --n 200000
    python scripts/train_concepts.py --labels data/processed/puzzles.parquet
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from moveexp.config import DEFAULT_SEED, PROCESSED_DIR, RAW_DIR, THEME_VOCAB
from moveexp.data.lichess import Puzzle, reservoir_sample, stream_puzzles
from moveexp.data.puzzle_themes import themes_from_tags
from moveexp.schema import theme_multi_hot

PUZZLE_RAW = RAW_DIR / "lichess_db_puzzle.csv.zst"
PUZZLE_PARQUET = PROCESSED_DIR / "puzzles.parquet"


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
    args = parser.parse_args(argv)

    if not args.puzzles.exists():
        raise SystemExit(f"{args.puzzles} not found; run scripts/download_data.py puzzles first")

    puzzles = reservoir_sample(stream_puzzles(args.puzzles), args.n, seed=args.seed)
    print(f"sampled {len(puzzles)} puzzles")
    rows = rows_from_puzzles(puzzles, all_solver_moves=args.all_solver_moves)
    if not rows:
        raise SystemExit("no usable rows; is this a puzzle CSV?")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(args.out, engine="pyarrow", index=False)

    counts = _prevalence(rows)
    print(f"wrote {len(rows)} rows to {args.out}")
    print(f"  distinct themes: {len(counts)} of {len(THEME_VOCAB)}")
    print("  most common:")
    for theme, count in counts.most_common(10):
        print(f"    {theme:<22} {count:>8}  ({count / len(rows):.1%})")
    print(f"next: python scripts/train_concepts.py --labels {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
