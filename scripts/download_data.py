#!/usr/bin/env python3
"""Download the corpora the project trains on, resumably.

Only the Lichess puzzle export is fetched by this milestone: it is small (~350 MB), CC0 and
carries independent, human-curated tactic tags, which is what the concept dataset and the
detector benchmark are built on. Games and the evaluation database are documented in
``docs/DATASETS.md`` and are deliberately out of scope here.

Run inside the venv::

    python scripts/download_data.py puzzles                 # -> data/raw/lichess_db_puzzle.csv.zst
    python scripts/download_data.py puzzles --force         # re-download from scratch

The download resumes: interrupt it and run it again, and it continues from ``<dest>.part``.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from moveexp.config import RAW_DIR
from moveexp.data.lichess import PUZZLE_URL, download

#: Default destination of the puzzle corpus.
PUZZLE_DEST = RAW_DIR / "lichess_db_puzzle.csv.zst"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    puzzles = sub.add_parser("puzzles", help="Download the Lichess puzzle database (~350 MB).")
    puzzles.add_argument("--url", default=PUZZLE_URL, help="Source URL (rarely changed).")
    puzzles.add_argument("--out", type=Path, default=PUZZLE_DEST, help="Destination file.")
    puzzles.add_argument(
        "--force", action="store_true", help="Delete an existing file and start over."
    )

    args = parser.parse_args(argv)

    if args.command == "puzzles":
        if args.force and args.out.exists():
            args.out.unlink()
        path = download(args.url, args.out, resume=True)
        print(f"puzzle corpus ready: {path}")
        print(f"next: python eval/puzzle_benchmark.py --puzzles {path} --n 20000")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
