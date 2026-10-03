"""Command-line interface (typer).

Global options (engine path, threads, hash) come *before* the sub-command; per-command
options (depth, nodes, multipv, cache) come after it::

    moveexp --engine-path /usr/games/stockfish analyze-move --fen "<FEN>" --move e2e4

Commands: ``analyze-move`` (one position), ``analyze-pgn`` (one game), ``batch`` (many games
to Parquet), ``vocab`` (the frozen label spaces). ``predict`` and ``explain`` arrive with
Stages 4 and 5.
"""

import io
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import chess
import chess.pgn
import typer

from .config import (
    DEFAULT_CACHE_DB,
    DEFAULT_DEPTH,
    DEFAULT_ENGINE_PATH,
    DEFAULT_HASH_MB,
    DEFAULT_MULTIPV,
    DEFAULT_THREADS,
    QUALITY_LABELS,
    THEME_VOCAB,
)
from .pipeline import analyse_game, analyse_move

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Explain the intent, tactical importance and positional effect of a chess move.",
)


class GlobalOptions:
    """Engine and path settings shared by every sub-command."""

    def __init__(
        self,
        engine_path: str = DEFAULT_ENGINE_PATH,
        threads: int = DEFAULT_THREADS,
        hash_mb: int = DEFAULT_HASH_MB,
        data_dir: Path | None = None,
    ) -> None:
        self.engine_path = engine_path
        self.threads = threads
        self.hash_mb = hash_mb
        self.data_dir = data_dir

    @property
    def cache_db(self) -> Path:
        """Default cache file, honouring ``--data-dir`` / ``MOVEXP_DATA_DIR``."""
        if self.data_dir is not None:
            return self.data_dir / "cache" / "engine_cache.sqlite3"
        return DEFAULT_CACHE_DB


@app.callback()
def main(
    ctx: typer.Context,
    engine_path: str = typer.Option(
        DEFAULT_ENGINE_PATH,
        "--engine-path",
        help="Path to the Stockfish binary (default: $STOCKFISH_PATH or 'stockfish').",
    ),
    threads: int = typer.Option(
        DEFAULT_THREADS, "--threads", min=1, help="UCI Threads. Keep 1 per worker process."
    ),
    hash_mb: int = typer.Option(DEFAULT_HASH_MB, "--hash", min=1, help="UCI Hash in MiB."),
    data_dir: Path | None = typer.Option(
        None,
        "--data-dir",
        help="Data directory (default: $MOVEXP_DATA_DIR or <repo>/data).",
    ),
) -> None:
    """Global options; must appear before the sub-command name."""
    ctx.obj = GlobalOptions(
        engine_path=engine_path, threads=threads, hash_mb=hash_mb, data_dir=data_dir
    )


def _limit(depth: int | None, nodes: int | None) -> Any:
    """Build an ``AnalysisLimit`` from mutually exclusive depth/node flags."""
    from .engine.client import AnalysisLimit

    if depth is not None and nodes is not None:
        raise typer.BadParameter("--depth and --nodes are mutually exclusive")
    if nodes is not None:
        return AnalysisLimit.by_nodes(nodes)
    return AnalysisLimit.by_depth(depth if depth is not None else DEFAULT_DEPTH)


def _resolve_move(board: chess.Board, move_uci: str) -> chess.Move:
    """Parse a UCI or SAN move and check it is legal in ``board``."""
    text = move_uci.strip()
    try:
        move = board.parse_uci(text)
    except ValueError:
        move = None
    if move is None:
        try:
            move = board.parse_san(text)
        except ValueError as exc:
            raise typer.BadParameter(
                f"{move_uci!r} is neither a legal UCI move nor SAN in this position"
            ) from exc
    if move not in board.legal_moves:
        raise typer.BadParameter(f"move {move.uci()} ({board.san(move)}) is not legal here")
    return move


def _parse_fen(fen: str) -> chess.Board:
    """Parse a FEN, turning python-chess' error into a CLI error."""
    try:
        return chess.Board(fen.strip())
    except ValueError as exc:
        raise typer.BadParameter(f"invalid FEN: {exc}") from exc


@app.command("analyze-move")
def analyze_move(
    ctx: typer.Context,
    fen: str = typer.Option(..., "--fen", help="FEN of the position before the move."),
    move: str = typer.Option(..., "--move", help="Move to analyse, UCI (e2e4) or SAN (e4)."),
    depth: int | None = typer.Option(
        None, "--depth", min=1, help=f"Search depth (default {DEFAULT_DEPTH})."
    ),
    nodes: int | None = typer.Option(
        None, "--nodes", min=1, help="Node budget; mutually exclusive with --depth."
    ),
    multipv: int = typer.Option(
        DEFAULT_MULTIPV, "--multipv", min=1, help=f"PV lines to return (default {DEFAULT_MULTIPV})."
    ),
    out: Path | None = typer.Option(None, "--out", help="Write the JSON report here."),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Indent the JSON output."),
    no_cache: bool = typer.Option(False, "--no-cache", help="Bypass the SQLite analysis cache."),
    cache_db: Path | None = typer.Option(
        None, "--cache-db", help="SQLite cache file (default data/cache/engine_cache.sqlite3)."
    ),
    null_move_probes: bool = typer.Option(
        False, "--null-move-probes", help="Run the optional engine threat probes (extra cost)."
    ),
) -> None:
    """Analyse a single move in a single position and print a MoveReport as JSON.

    Example::

        moveexp analyze-move --fen "<FEN>" --move e2e4
    """
    options: GlobalOptions = ctx.obj or GlobalOptions()
    board = _parse_fen(fen)
    parsed_move = _resolve_move(board, move)
    report = analyse_move(
        board,
        parsed_move,
        engine_path=options.engine_path,
        threads=options.threads,
        hash_mb=options.hash_mb,
        limit=_limit(depth, nodes),
        multipv=multipv,
        cache_db=cache_db or options.cache_db,
        use_cache=not no_cache,
        null_move_probes=null_move_probes,
    )
    payload = json.dumps(report.model_dump(mode="json"), indent=2 if pretty else None)
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload + "\n", encoding="utf-8")
        typer.echo(f"wrote {out}")
    else:
        typer.echo(payload)


@app.command("analyze-pgn")
def analyze_pgn(
    ctx: typer.Context,
    game_path: Path = typer.Argument(..., help="PGN file (the first game is analysed)."),
    depth: int | None = typer.Option(
        None, "--depth", min=1, help=f"Search depth (default {DEFAULT_DEPTH})."
    ),
    nodes: int | None = typer.Option(
        None, "--nodes", min=1, help="Node budget; mutually exclusive with --depth."
    ),
    multipv: int = typer.Option(DEFAULT_MULTIPV, "--multipv", min=1, help="PV lines to return."),
    out: Path | None = typer.Option(None, "--out", help="Write the JSON report here."),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Indent the JSON output."),
    no_cache: bool = typer.Option(False, "--no-cache", help="Bypass the SQLite analysis cache."),
    cache_db: Path | None = typer.Option(None, "--cache-db", help="SQLite cache file."),
    max_plies: int = typer.Option(
        0, "--max-plies", min=0, help="Analyse at most this many plies (0 = all)."
    ),
) -> None:
    """Analyse the first game of a PGN and print a GameReport as JSON."""
    options: GlobalOptions = ctx.obj or GlobalOptions()
    with game_path.open() as handle:
        game = chess.pgn.read_game(handle)
    if game is None:
        raise typer.BadParameter(f"no game found in {game_path}")

    report = analyse_game(
        game,
        engine_path=options.engine_path,
        threads=options.threads,
        hash_mb=options.hash_mb,
        limit=_limit(depth, nodes),
        multipv=multipv,
        cache_db=cache_db or options.cache_db,
        use_cache=not no_cache,
        max_plies=max_plies,
    )
    payload = json.dumps(report.model_dump(mode="json"), indent=2 if pretty else None)
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload + "\n", encoding="utf-8")
        typer.echo(f"wrote {out}")
    else:
        typer.echo(payload)


def _batch_worker(payload: tuple[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Reconstruct one game from PGN text and return its flat labelled rows (worker)."""
    pgn_text, kwargs = payload
    game = chess.pgn.read_game(io.StringIO(pgn_text))
    return analyse_game(game, **kwargs).to_flat_rows()


@app.command("batch")
def batch(
    ctx: typer.Context,
    games: Path = typer.Argument(..., help="PGN file with one or more games."),
    out: Path = typer.Option(..., "--out", help="Parquet file to write."),
    workers: int = typer.Option(1, "--workers", min=1, help="Engine processes to run in parallel."),
    depth: int | None = typer.Option(
        None, "--depth", min=1, help=f"Search depth (default {DEFAULT_DEPTH})."
    ),
    nodes: int | None = typer.Option(
        None, "--nodes", min=1, help="Node budget; mutually exclusive with --depth."
    ),
    multipv: int = typer.Option(DEFAULT_MULTIPV, "--multipv", min=1, help="PV lines to return."),
    no_cache: bool = typer.Option(False, "--no-cache", help="Bypass the SQLite analysis cache."),
    cache_db: Path | None = typer.Option(None, "--cache-db", help="SQLite cache file."),
    max_plies: int = typer.Option(
        0, "--max-plies", min=0, help="Analyse at most this many plies per game (0 = all)."
    ),
) -> None:
    """Analyse every game in a PGN and write one labelled row per move to Parquet."""
    from tqdm import tqdm

    options: GlobalOptions = ctx.obj or GlobalOptions()
    kwargs: dict[str, Any] = {
        "engine_path": options.engine_path,
        "threads": options.threads,
        "hash_mb": options.hash_mb,
        "limit": _limit(depth, nodes),
        "multipv": multipv,
        "cache_db": cache_db or options.cache_db,
        "use_cache": not no_cache,
        "max_plies": max_plies,
    }

    pgn_texts: list[str] = []
    with games.open() as handle:
        while (game := chess.pgn.read_game(handle)) is not None:
            pgn_texts.append(str(game))
    if not pgn_texts:
        raise typer.BadParameter(f"no games found in {games}")

    rows: list[dict[str, Any]] = []
    if workers <= 1:
        for text in tqdm(pgn_texts, desc="analysing games"):
            rows.extend(_batch_worker((text, kwargs)))
    else:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            results = executor.map(_batch_worker, [(text, kwargs) for text in pgn_texts])
            for result in tqdm(results, desc="analysing games", total=len(pgn_texts)):
                rows.extend(result)

    import pandas as pd

    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(out, engine="pyarrow", index=False)
    typer.echo(f"wrote {len(rows)} rows to {out}")


@app.command("vocab")
def vocab() -> None:
    """Print the frozen label vocabularies (useful to check a dataset's columns)."""
    payload = {
        "quality_labels": list(QUALITY_LABELS),
        "theme_vocab": list(THEME_VOCAB),
        "theme_vocab_size": len(THEME_VOCAB),
    }
    typer.echo(json.dumps(payload, indent=2))


def main_entry() -> None:  # pragma: no cover - console-script shim
    """Entry point used by the ``moveexp`` console script."""
    app()


if __name__ == "__main__":  # pragma: no cover
    main_entry()
