#!/usr/bin/env python3
"""Generate a small self-play PGN for the neural baseline, using only a local engine.

Stockfish plays short games against itself at low depth, sampling among its top few moves
so the corpus is diverse (not one deterministic line). Nothing is downloaded. The PGN is
then labelled with ``moveexp batch``.

Run inside the venv::

    .venv\\Scripts\\python.exe scripts/generate_games.py --games 40 --max-plies 50
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path

import chess
import chess.engine
import chess.pgn

from moveexp.config import DEFAULT_ENGINE_PATH, RAW_DIR


def _sample_move(
    engine: chess.engine.SimpleEngine,
    board: chess.Board,
    depth: int,
    width: int,
    rng: random.Random,
) -> chess.Move:
    """Pick a move biased towards the engine's best but allowing the top ``width``."""
    width = max(1, min(width, board.legal_moves.count()))
    infos = engine.analyse(board, chess.engine.Limit(depth=depth), multipv=width)
    if isinstance(infos, dict):  # python-chess returns a list when multipv > 1
        infos = [infos]
    moves = [info["pv"][0] for info in infos if info.get("pv")]
    if not moves:
        return next(iter(board.legal_moves))
    weights = [0.55**i for i in range(len(moves))]
    return rng.choices(moves, weights=weights, k=1)[0]


def play_game(
    engine: chess.engine.SimpleEngine,
    rng: random.Random,
    max_plies: int,
    depth: int,
    width: int,
) -> chess.pgn.Game:
    """Play one self-play game and return it as a PGN game."""
    board = chess.Board()
    game = chess.pgn.Game()
    game.headers["Event"] = "moveexp self-play"
    game.headers["White"] = "Stockfish-self"
    game.headers["Black"] = "Stockfish-self"
    node: chess.pgn.GameNode = game
    for _ in range(max_plies):
        if board.is_game_over(claim_draw=True):
            break
        move = _sample_move(engine, board, depth, width, rng)
        node = node.add_variation(move)
        board.push(move)
    game.headers["Result"] = board.result(claim_draw=True)
    return game


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--games", type=int, default=40)
    parser.add_argument("--max-plies", type=int, default=50)
    parser.add_argument("--depth", type=int, default=6, help="Self-play search depth.")
    parser.add_argument("--width", type=int, default=3, help="Sample among this many top moves.")
    parser.add_argument("--seed", type=int, default=20240917)
    parser.add_argument("--engine-path", default=DEFAULT_ENGINE_PATH)
    parser.add_argument("--out", type=Path, default=RAW_DIR / "selfplay.pgn")
    args = parser.parse_args(argv)

    rng = random.Random(args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    engine = chess.engine.SimpleEngine.popen_uci(args.engine_path)
    try:
        with args.out.open("w", encoding="utf-8") as handle:
            for index in range(args.games):
                game = play_game(engine, rng, args.max_plies, args.depth, args.width)
                # python-chess defaults Site to "?", and moveexp._game_id uses Site as the
                # game id when present, so a unique Site keeps games separable in the split.
                game.headers["Site"] = f"moveexp-selfplay-{index:04d}"
                handle.write(str(game) + "\n\n")
                print(f"game {index + 1}/{args.games}: {len(list(game.mainline_moves()))} plies")
    finally:
        engine.quit()
    print(f"wrote {args.games} games to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
