#!/usr/bin/env python3
"""Build the demo artefacts: explain every game under ``demo/games`` and write text + JSON.

Each game becomes a Markdown narration (``demo/out/<name>.md``) and a structured JSON
dump (``demo/out/<name>.json``) holding the full reports and their verified explanations.
The Markdown is the human-readable story; the JSON is what the gallery and any later
analysis read.

Run inside the venv::

    .venv\\Scripts\\python.exe scripts/build_demo.py --depth 12
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import chess.pgn

from moveexp.config import DEFAULT_CACHE_DB, DEFAULT_ENGINE_PATH, PROJECT_ROOT
from moveexp.engine.client import AnalysisLimit
from moveexp.explain import explain_game, format_game_explanation

DEMO_DIR = PROJECT_ROOT / "demo"
GAMES_DIR = DEMO_DIR / "games"
OUT_DIR = DEMO_DIR / "out"


def build_one(
    game_path: Path,
    out_dir: Path,
    *,
    depth: int,
    multipv: int,
    engine_path: str,
    cache_db: Path,
) -> dict[str, object]:
    """Explain one PGN game and write its Markdown + JSON artefacts."""
    with game_path.open(encoding="utf-8") as handle:
        game = chess.pgn.read_game(handle)
    if game is None:
        raise SystemExit(f"no game found in {game_path}")

    result = explain_game(
        game,
        engine_path=engine_path,
        limit=AnalysisLimit.by_depth(depth),
        multipv=multipv,
        cache_db=cache_db,
        use_cache=True,
    )

    stem = game_path.stem
    md_path = out_dir / f"{stem}.md"
    json_path = out_dir / f"{stem}.json"
    md_path.write_text(format_game_explanation(result), encoding="utf-8")
    json_path.write_text(
        json.dumps(
            {
                "headers": {str(k): str(v) for k, v in game.headers.items()},
                "game": result.game.model_dump(mode="json"),
                "explanations": [e.model_dump(mode="json") for e in result.explanations],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return {"stem": stem, "plies": len(result.explanations), "md": md_path, "json": json_path}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--depth", type=int, default=12, help="Search depth per move.")
    parser.add_argument("--multipv", type=int, default=3, help="MultiPV width.")
    parser.add_argument("--engine-path", default=DEFAULT_ENGINE_PATH)
    parser.add_argument("--cache-db", type=Path, default=DEFAULT_CACHE_DB)
    parser.add_argument("--games", type=Path, default=GAMES_DIR)
    parser.add_argument("--out", type=Path, default=OUT_DIR)
    args = parser.parse_args(argv)

    args.out.mkdir(parents=True, exist_ok=True)
    games = sorted(args.games.glob("*.pgn"))
    if not games:
        raise SystemExit(f"no .pgn files in {args.games}")

    for game_path in games:
        info = build_one(
            game_path,
            args.out,
            depth=args.depth,
            multipv=args.multipv,
            engine_path=args.engine_path,
            cache_db=args.cache_db,
        )
        print(f"{info['stem']}: {info['plies']} plies -> {info['md']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
