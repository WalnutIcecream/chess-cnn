#!/usr/bin/env python3
"""Run the pipeline live on one position and print the verified explanation.

Zero-argument by default: with no options it analyses a built-in showcase move — Morphy's
10.Nxb5 from the demo corpus, or a hard-coded mate-in-one if that corpus is missing — prints
the verified explanation, writes a JSON report (report + explanation + claims), and renders a
board PNG with the detected theme squares coloured.

    .venv\\Scripts\\python.exe scripts/demo_run.py
    .venv\\Scripts\\python.exe scripts/demo_run.py --fen "<FEN>" --move Nxb5
    .venv\\Scripts\\python.exe scripts/demo_run.py --pgn demo/games/opera.pgn

The engine is located automatically (``STOCKFISH_PATH``, then the repo's ``tools/`` drop, then
``stockfish`` on PATH), so the zero-argument form needs no environment setup.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import sys
from pathlib import Path

import chess

from moveexp.config import PROJECT_ROOT
from moveexp.engine.client import AnalysisLimit
from moveexp.explain import explain_game, explain_move, format_move_explanation

DEMO_DIR = PROJECT_ROOT / "demo"
LIVE_DIR = DEMO_DIR / "live"
OPERA_JSON = DEMO_DIR / "out" / "opera.json"

#: Fallback when the demo corpus is missing: the mate-in-one Qxf7#.
FALLBACK_FEN = "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 4 4"
FALLBACK_MOVE = "f3f7"

#: Unicode chess glyphs (DejaVu Sans, the matplotlib default, provides them).
PIECE_GLYPH = {
    "P": "\u2659",
    "N": "\u2658",
    "B": "\u2657",
    "R": "\u2656",
    "Q": "\u2655",
    "K": "\u2654",
    "p": "\u265f",
    "n": "\u265e",
    "b": "\u265d",
    "r": "\u265c",
    "q": "\u265b",
    "k": "\u265a",
}


def _force_utf8() -> None:
    """Print UTF-8 on the console regardless of the Windows locale (the text has em dashes)."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        with contextlib.suppress(ValueError, OSError):
            reconfigure(encoding="utf-8")


def find_engine() -> str:
    """Locate a Stockfish binary: ``STOCKFISH_PATH``, then the repo ``tools/`` drop, then PATH."""
    env = os.environ.get("STOCKFISH_PATH")
    if env and Path(env).exists():
        return env
    for pattern in ("**/stockfish*.exe", "**/stockfish"):
        for candidate in sorted((PROJECT_ROOT / "tools").glob(pattern)):
            if candidate.is_file():
                return str(candidate)
    return env or "stockfish"


def load_showcase(path: Path = OPERA_JSON, ply: int = 18) -> tuple[str, str, str]:
    """Return ``(fen, move_uci, description)`` for the built-in showcase move."""
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        headers = data.get("headers", {})
        for report in data.get("game", {}).get("moves", []):
            if int(report["ply"]) == ply:
                white = headers.get("White", "?")
                black = headers.get("Black", "?")
                return (
                    report["fen_before"],
                    report["move_uci"],
                    f"{white} vs {black}, ply {ply} ({report['move_san']})",
                )
    return FALLBACK_FEN, FALLBACK_MOVE, "built-in mate-in-one (demo corpus not found)"


def resolve_move(board: chess.Board, text: str) -> chess.Move:
    """Parse a UCI or SAN move and check it is legal."""
    stripped = text.strip()
    try:
        move = board.parse_uci(stripped)
    except ValueError:
        try:
            move = board.parse_san(stripped)
        except ValueError as exc:
            raise SystemExit(f"{text!r} is neither a legal UCI move nor SAN here") from exc
    if move not in board.legal_moves:
        raise SystemExit(f"move {move.uci()} is not legal in this position")
    return move


def render_board_png(path: Path, fen: str, uci: str, theme_squares: list[str]) -> Path:
    """Draw the board to a PNG: theme squares blue, the played move yellow + an arrow."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.patheffects as path_effects
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch

    board = chess.Board(fen)
    theme: set[chess.Square] = set()
    for name in theme_squares:
        try:
            theme.add(chess.parse_square(name))
        except ValueError:
            continue
    try:
        move = chess.Move.from_uci(uci)
    except ValueError:
        move = None

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 8)
    ax.set_aspect("equal")
    ax.axis("off")
    for rank in range(8):
        for file in range(8):
            square = chess.square(file, rank)
            color = "#f0d9b5" if (file + rank) % 2 else "#b58863"
            if square in theme:
                color = "#bcd4ea"
            if move is not None and square in (move.from_square, move.to_square):
                color = "#f6e58d"
            ax.add_patch(plt.Rectangle((file, rank), 1, 1, facecolor=color, edgecolor="none"))
    for square, piece in board.piece_map().items():
        file = chess.square_file(square)
        rank = chess.square_rank(square)
        white = piece.color == chess.WHITE
        text = ax.text(
            file + 0.5,
            rank + 0.5,
            PIECE_GLYPH[piece.symbol()],
            ha="center",
            va="center",
            fontsize=27,
            color="#ffffff" if white else "#111111",
        )
        text.set_path_effects(
            [path_effects.withStroke(linewidth=1.4, foreground="#111111" if white else "#ffffff")]
        )
    if move is not None:
        start = (
            chess.square_file(move.from_square) + 0.5,
            chess.square_rank(move.from_square) + 0.5,
        )
        end = (chess.square_file(move.to_square) + 0.5, chess.square_rank(move.to_square) + 0.5)
        ax.add_patch(
            FancyArrowPatch(
                start,
                end,
                arrowstyle="-|>",
                mutation_scale=20,
                linewidth=3.5,
                color="#2b7a4b",
                alpha=0.9,
            )
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="#12151b")
    plt.close(fig)
    return path


def payload(description: str, report, explanation) -> dict:
    """The JSON written beside the board: what it was, the report, and the verified prose."""
    return {
        "description": description,
        "report": report.model_dump(mode="json"),
        "explanation": explanation.model_dump(mode="json"),
    }


def output_paths(out_dir: Path, name: str) -> tuple[Path, Path]:
    """Create ``out_dir`` if needed and return the ``(json, png)`` paths."""
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / f"{name}.json", out_dir / f"{name}.png"


def _run_single(args: argparse.Namespace, out_dir: Path) -> int:
    if args.fen and args.move:
        fen, uci, description = args.fen, args.move, "supplied position"
    else:
        fen, uci, description = load_showcase()
    board = chess.Board(fen)
    move = resolve_move(board, uci)
    result = explain_move(
        board,
        move,
        engine_path=find_engine(),
        limit=AnalysisLimit.by_depth(args.depth),
        multipv=args.multipv,
        use_cache=not args.no_cache,
    )
    print(f"# {description}")
    print(format_move_explanation(result))
    squares = sorted({s for hit in result.report.themes for s in hit.squares})
    json_path, png_path = output_paths(out_dir, args.name or "showcase")
    json_path.write_text(
        json.dumps(payload(description, result.report, result.explanation), indent=2),
        encoding="utf-8",
    )
    render_board_png(png_path, fen, result.report.move_uci, squares)
    print(f"\nreport: {json_path}")
    print(f"board:  {png_path}")
    return 0


def _run_pgn(args: argparse.Namespace, out_dir: Path) -> int:
    import chess.pgn

    with args.pgn.open(encoding="utf-8") as handle:
        game = chess.pgn.read_game(handle)
    if game is None:
        raise SystemExit(f"no game found in {args.pgn}")
    result = explain_game(
        game,
        engine_path=find_engine(),
        limit=AnalysisLimit.by_depth(args.depth),
        multipv=args.multipv,
        use_cache=not args.no_cache,
    )
    for move in result.explanations:
        number = move.ply // 2 + 1
        dots = "." if move.ply % 2 == 0 else "..."
        print(f"{number}{dots} {move.headline}")
    name = args.name or args.pgn.stem
    json_path, _ = output_paths(out_dir, name)
    json_path.write_text(
        json.dumps(
            {
                "game": result.game.model_dump(mode="json"),
                "explanations": [e.model_dump(mode="json") for e in result.explanations],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nreport: {json_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fen", help="Position FEN (with --move) instead of the showcase.")
    parser.add_argument("--move", help="Move to explain, UCI or SAN.")
    parser.add_argument("--pgn", type=Path, help="Explain every move of the first game in a PGN.")
    parser.add_argument("--depth", type=int, default=14)
    parser.add_argument("--multipv", type=int, default=3)
    parser.add_argument("--out-dir", type=Path, default=LIVE_DIR)
    parser.add_argument(
        "--name", default=None, help="Output basename (default: showcase / pgn stem)."
    )
    parser.add_argument("--no-cache", action="store_true")
    args = parser.parse_args(argv)

    _force_utf8()
    if args.move and not args.fen:
        raise SystemExit("--move needs --fen")
    out_dir = args.out_dir
    if args.pgn is not None:
        return _run_pgn(args, out_dir)
    return _run_single(args, out_dir)


if __name__ == "__main__":
    raise SystemExit(main())
