"""Benchmark the theme detectors against the Lichess puzzle tags.

A Lichess puzzle is a FEN plus a move list: the first move is the opponent's blunder that
*creates* the puzzle, and the rest is the solution line (the solver's moves alternating with
the forced replies). This script:

1. applies the first move to reach the puzzle position,
2. runs the registered detectors on the *solver's* moves of the solution, handing them the
   remaining solution as the continuation (so line-aware motifs such as ``attraction`` and
   ``intermezzo`` are measurable too),
3. maps the puzzle's Lichess tags to our theme names
   (:data:`moveexp.data.puzzle_themes.PUZZLE_TAG_TO_THEME`),
4. reports precision / recall / F1 per theme to a CSV.

The tags come from Lichess, not from our detectors, so agreement between the two is real
signal about detector quality rather than a tautology. Reads the ``.zst`` export directly.

Usage::

    python eval/puzzle_benchmark.py --puzzles data/raw/lichess_db_puzzle.csv.zst \
        --n 20000 --seed 20240917 --out data/audit/puzzle_benchmark.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections.abc import Sequence
from pathlib import Path

# Make the source tree importable when the script is run directly from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from moveexp.analysis.themes import register_all  # noqa: E402
from moveexp.analysis.themes.base import DetectionContext, run_all  # noqa: E402
from moveexp.config import THEME_VOCAB  # noqa: E402
from moveexp.data.lichess import Puzzle, reservoir_sample, stream_puzzles  # noqa: E402
from moveexp.data.puzzle_themes import PUZZLE_TAG_TO_THEME  # noqa: E402

#: The measurable themes, in vocabulary order (deterministic output).
THEMES: tuple[str, ...] = tuple(
    theme for theme in THEME_VOCAB if theme in set(PUZZLE_TAG_TO_THEME.values())
)


def detected_themes(puzzle: Puzzle) -> set[str]:
    """Run the detectors on the puzzle's solution and return the union of theme names."""
    try:
        board = puzzle.position_after_blunder()
    except ValueError:
        return set()
    moves = puzzle.solution_moves()
    found: set[str] = set()
    for index, move in enumerate(moves):
        if move not in board.legal_moves:
            break
        if index % 2 == 0:  # the solver's moves (indices 0, 2, 4, ... of the solution)
            context = DetectionContext.from_move(board, move, continuation=moves[index + 1 :])
            found.update(hit.theme for hit in run_all(context))
        board.push(move)
    return found


def evaluate(
    puzzles: Sequence[Puzzle], themes: Sequence[str] = THEMES
) -> list[dict[str, float | int | str]]:
    """Precision / recall / F1 per theme across ``puzzles``."""
    register_all()
    wanted = tuple(themes)
    counts = {theme: {"tp": 0, "fp": 0, "fn": 0, "gold": 0} for theme in wanted}
    for puzzle in puzzles:
        gold = {PUZZLE_TAG_TO_THEME[tag] for tag in puzzle.themes if tag in PUZZLE_TAG_TO_THEME}
        detected = detected_themes(puzzle)
        for theme in wanted:
            counts[theme]["gold"] += int(theme in gold)
            in_gold, in_det = theme in gold, theme in detected
            if in_gold and in_det:
                counts[theme]["tp"] += 1
            elif in_det:
                counts[theme]["fp"] += 1
            elif in_gold:
                counts[theme]["fn"] += 1

    rows: list[dict[str, float | int | str]] = []
    for theme in wanted:
        c = counts[theme]
        tp, fp, fn = c["tp"], c["fp"], c["fn"]
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        rows.append(
            {
                "theme": theme,
                "gold": c["gold"],
                "detected": tp + fp,
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1": round(f1, 4),
            }
        )
    return rows


def _write_csv(rows: Sequence[dict[str, float | int | str]], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _print_table(rows: Sequence[dict[str, float | int | str]]) -> None:
    ranked = sorted(rows, key=lambda r: (r["f1"], r["gold"]), reverse=True)
    print(f"{'theme':<22} {'gold':>7} {'det':>7} {'P':>6} {'R':>6} {'F1':>6}")
    for row in ranked:
        print(
            f"{row['theme']:<22} {row['gold']:>7} {row['detected']:>7} "
            f"{row['precision']:>6.2f} {row['recall']:>6.2f} {row['f1']:>6.2f}"
        )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--puzzles", required=True, type=Path, help="Puzzle CSV (.zst ok).")
    parser.add_argument("--n", type=int, default=20000, help="How many puzzles to sample.")
    parser.add_argument("--seed", type=int, default=20240917, help="Sampling seed.")
    parser.add_argument("--out", type=Path, default=Path("data/audit/puzzle_benchmark.csv"))
    parser.add_argument(
        "--themes",
        default="",
        help="Comma-separated subset of themes to report (default: all measurable).",
    )
    args = parser.parse_args(argv)

    themes = [t.strip() for t in args.themes.split(",") if t.strip()] or list(THEMES)
    puzzles = reservoir_sample(stream_puzzles(args.puzzles), args.n, seed=args.seed)
    rows = evaluate(puzzles, themes)
    _write_csv(rows, args.out)
    _print_table(rows)
    gold_total = sum(row["gold"] for row in rows if row["theme"] in themes)
    print(f"\nevaluated {len(puzzles)} puzzles ({gold_total} tagged tactics); wrote {args.out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
