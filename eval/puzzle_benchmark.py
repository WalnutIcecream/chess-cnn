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
from moveexp.data.puzzle_themes import PUZZLE_TAG_TO_THEME, theme_group  # noqa: E402

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
                "group": theme_group(theme) or "other",
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


def group_scores(rows: Sequence[dict[str, float | int | str]]) -> dict[str, dict[str, float | int]]:
    """Aggregate the per-theme counts into micro and macro scores per tag group.

    Micro pools every ``(theme, puzzle)`` decision in the group, so it answers "how good are
    these detectors overall"; macro is the mean of the per-theme F1, so it answers "how good is
    the average detector". They disagree, and both are reported for that reason.
    """
    totals: dict[str, list[int]] = {}
    f1s: dict[str, list[float]] = {}
    for row in rows:
        group = str(row["group"])
        acc = totals.setdefault(group, [0, 0, 0])
        acc[0] += int(row["tp"])
        acc[1] += int(row["fp"])
        acc[2] += int(row["fn"])
        f1s.setdefault(group, []).append(float(row["f1"]))

    scores: dict[str, dict[str, float | int]] = {}
    for group, (tp, fp, fn) in sorted(totals.items()):
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        micro = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        scores[group] = {
            "themes": len(f1s[group]),
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "micro_precision": round(precision, 4),
            "micro_recall": round(recall, 4),
            "micro_f1": round(micro, 4),
            "macro_f1": round(sum(f1s[group]) / len(f1s[group]), 4),
        }
    return scores


def _write_csv(rows: Sequence[dict[str, float | int | str]], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _print_table(rows: Sequence[dict[str, float | int | str]]) -> None:
    """Print the per-theme table, grouped by move-level / puzzle-level."""
    for group in ("move", "puzzle", "other"):
        group_rows = [row for row in rows if row["group"] == group]
        if not group_rows:
            continue
        print(f"\n=== {group}-level themes ===")
        print(f"{'theme':<22} {'gold':>7} {'det':>7} {'P':>6} {'R':>6} {'F1':>6}")
        for row in sorted(group_rows, key=lambda r: (r["f1"], r["gold"]), reverse=True):
            print(
                f"{row['theme']:<22} {row['gold']:>7} {row['detected']:>7} "
                f"{row['precision']:>6.2f} {row['recall']:>6.2f} {row['f1']:>6.2f}"
            )


def _print_group_summary(rows: Sequence[dict[str, float | int | str]]) -> None:
    """Print the micro/macro scores per group -- the headline the per-theme table hides."""
    print("\n=== group summary ===")
    print(f"{'group':<8} {'themes':>6} {'P':>7} {'R':>7} {'microF1':>8} {'macroF1':>8}")
    for group, score in group_scores(rows).items():
        print(
            f"{group:<8} {score['themes']:>6} {score['micro_precision']:>7.3f} "
            f"{score['micro_recall']:>7.3f} {score['micro_f1']:>8.3f} {score['macro_f1']:>8.3f}"
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
    _print_group_summary(rows)
    gold_total = sum(row["gold"] for row in rows if row["theme"] in themes)
    print(f"\nevaluated {len(puzzles)} puzzles ({gold_total} tagged tactics); wrote {args.out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
