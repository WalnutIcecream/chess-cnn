"""Tests for the live demo runner (``scripts/demo_run.py``).

The module is loaded by path. Pure helpers (showcase loading, move resolution, board
rendering, output paths, JSON payload) are tested here; the engine path is left to the CLI
smoke run.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import chess
import pytest

ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location("demo_run", ROOT / "scripts" / "demo_run.py")
assert _SPEC is not None and _SPEC.loader is not None
dr = importlib.util.module_from_spec(_SPEC)
sys.modules["demo_run"] = dr
_SPEC.loader.exec_module(dr)


def test_load_showcase_falls_back_when_missing(tmp_path: Path) -> None:
    fen, uci, description = dr.load_showcase(tmp_path / "nope.json")
    assert fen == dr.FALLBACK_FEN and uci == dr.FALLBACK_MOVE
    assert "corpus" in description
    assert chess.Move.from_uci(uci) in chess.Board(fen).legal_moves


def test_load_showcase_reads_a_real_dump(tmp_path: Path) -> None:
    data = {
        "headers": {"White": "Morphy", "Black": "Duke"},
        "game": {
            "moves": [
                {"ply": 18, "fen_before": chess.STARTING_FEN, "move_uci": "e2e4", "move_san": "e4"}
            ]
        },
    }
    path = tmp_path / "g.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    fen, uci, description = dr.load_showcase(path, ply=18)
    assert uci == "e2e4"
    assert "Morphy" in description and "ply 18" in description


def test_resolve_move_accepts_uci_and_san() -> None:
    board = chess.Board()
    assert dr.resolve_move(board, "e2e4").uci() == "e2e4"
    assert dr.resolve_move(board, "e4").uci() == "e2e4"


def test_resolve_move_rejects_illegal() -> None:
    with pytest.raises(SystemExit):
        dr.resolve_move(chess.Board(), "e2e5")


def test_output_paths_creates_directory(tmp_path: Path) -> None:
    out = tmp_path / "nested" / "live"
    json_path, png_path = dr.output_paths(out, "showcase")
    assert out.is_dir()
    assert json_path.name == "showcase.json" and png_path.name == "showcase.png"


def test_render_board_png_writes_a_png(tmp_path: Path) -> None:
    path = tmp_path / "board.png"
    dr.render_board_png(path, chess.STARTING_FEN, "e2e4", ["d5", "f7", "not-a-square"])
    assert path.exists() and path.stat().st_size > 1000
    assert path.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_payload_shape() -> None:
    class _Model:
        def model_dump(self, mode: str = "json") -> dict:  # noqa: ARG002
            return {"kind": "model"}

    dumped = dr.payload("desc", _Model(), _Model())
    assert list(dumped) == ["description", "report", "explanation"]
    assert dumped["description"] == "desc"
    assert dumped["report"] == {"kind": "model"}
