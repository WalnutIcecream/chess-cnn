"""Benchmark the theme detectors against Lichess puzzle tags.

A Lichess puzzle is a FEN plus a move list: the first move is the opponent's blunder that
*creates* the puzzle, and the rest is the solution line (solver's moves alternating with the
opponent's forced replies). This script:

1. applies the first move to reach the puzzle position,
2. runs the registered detectors on the *solver's* moves of the solution,
3. maps the puzzle's Lichess tags to our theme names,
4. reports precision / recall / F1 per theme to a CSV.

The detectors are the ground truth being *measured*, not the source of truth: a Lichess
puzzle tag is an independent (human/vote-based) label, so agreement between the two is a real
signal about detector quality.

Usage::

    python eval/puzzle_benchmark.py --puzzles lichess_db_puzzle.csv.zst \
        --n 5000 --seed 20240917 --out data/audit/puzzle_benchmark.csv

Pass a plain CSV (already decompressed); the streaming ``.zst`` reader lives in
``scripts/download_data.py`` / ``data/lichess_io.py`` (Milestone 5).
"""

from __future__ import annotations

import argparse
import csv
import random
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import chess

# Make the source tree importable when the script is run directly from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from moveexp.analysis.themes import detect, register_all  # noqa: E402
from moveexp.schema import split_fen  # noqa: E402

#: Lichess tag -> our theme name. Only tags with a direct detector counterpart are measured.
TAG_TO_THEME: dict[str, str] = {
    "fork": "fork",
    "pin": "pin",
    "skewer": "skewer",
    "discoveredAttack": "discovered_attack",
    "hangingPiece": "hanging_piece",
    "backRankMate": "back_rank_mate",
    "sacrifice": "sacrifice",
    "trappedPiece": "trapped_piece",
    "promotion": "promotion",
    "deflection": "deflection",
    "interference": "interference",
    "xRayAttack": "x_ray",
    "doubleCheck": "double_check",
    "overloading": "overloaded_defender",
}

THEMES: tuple[str, ...] = tuple(dict.fromkeys(TAG_TO_THEME.values()))


@dataclass(frozen=True)
class Puzzle:
    """One puzzle reduced to the fields the benchmark needs."""

    puzzle_id: str
    fen: str
    moves: tuple[str, ...]
    themes: tuple[str, ...]


def parse_board(fen: str) -> chess.Board:
    """Parse a puzzle FEN, tolerating the missing halfmove/fullmove counters."""
    try:
        return chess.Board(fen.strip())
    except ValueError:
        placement, side, castling, ep, halfmove, fullmove = split_fen(fen)
        return chess.Board(f"{placement} {side} {castling} {ep} {halfmove} {fullmove}")


def parse_row(row: dict[str, str]) -> Puzzle | None:
    """Turn one CSV row into a :class:`Puzzle`, or ``None`` if it is unusable."""
    fen = (row.get("FEN") or "").strip()
    moves = (row.get("Moves") or "").split()
    if not fen or len(moves) < 2:
        return None
    return Puzzle(
        puzzle_id=row.get("PuzzleId", ""),
        fen=fen,
        moves=tuple(moves),
        themes=tuple((row.get("Themes") or "").split()),
    )


def detected_themes(puzzle: Puzzle) -> set[str]:
    """Run the detectors on the puzzle's solution and return the union of theme names."""
    board = parse_board(puzzle.fen)
    moves = [chess.Move.from_uci(uci) for uci in puzzle.moves]
    if moves[0] not in board.legal_moves:
        return set()
    board.push(moves[0])
    found: set[str] = set()
    for index in range(1, len(moves)):
        move = moves[index]
        if move not in board.legal_moves:
            break
        if index % 2 == 1:  # the solver's moves (indices 1, 3, 5, ...)
            found.update(hit.theme for hit in detect(board, move))
        board.push(move)
    return found


def evaluate(puzzles: Sequence[Puzzle]) -> list[dict[str, float | int | str]]:
    """Precision / recall / F1 per theme across ``puzzles``."""
    register_all()
    counts = {theme: {"tp": 0, "fp": 0, "fn": 0, "gold": 0} for theme in THEMES}
    for puzzle in puzzles:
        gold = {TAG_TO_THEME[tag] for tag in puzzle.themes if tag in TAG_TO_THEME}
        detected = detected_themes(puzzle)
        for theme in THEMES:
            counts[theme]["gold"] += int(theme in gold)
            in_gold, in_det = theme in gold, theme in detected
            if in_gold and in_det:
                counts[theme]["tp"] += 1
            elif in_det:
                counts[theme]["fp"] += 1
            elif in_gold:
                counts[theme]["fn"] += 1

    rows: list[dict[str, float | int | str]] = []
    for theme in THEMES:
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


def stream_puzzles(path: Path, n: int, seed: int) -> list[Puzzle]:
    """Reservoir-sample ``n`` puzzles from a CSV (constant memory, fixed seed)."""
    rng = random.Random(seed)
    sample: list[Puzzle] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for seen, row in enumerate(reader):
            puzzle = parse_row(row)
            if puzzle is None:
                continue
            if len(sample) < n:
                sample.append(puzzle)
            else:
                slot = rng.randint(0, seen)
                if slot < n:
                    sample[slot] = puzzle
    return sample


def _write_csv(rows: Sequence[dict[str, float | int | str]], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--puzzles", required=True, type=Path, help="Puzzle CSV file.")
    parser.add_argument("--n", type=int, default=5000, help="How many puzzles to sample.")
    parser.add_argument("--seed", type=int, default=20240917, help="Sampling seed.")
    parser.add_argument("--out", type=Path, default=Path("data/audit/puzzle_benchmark.csv"))
    args = parser.parse_args(argv)

    puzzles = stream_puzzles(args.puzzles, args.n, args.seed)
    rows = evaluate(puzzles)
    _write_csv(rows, args.out)
    print(f"evaluated {len(puzzles)} puzzles; wrote {args.out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
