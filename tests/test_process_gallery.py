"""Tests for the process gallery builder (``scripts/make_process_gallery.py``).

The builder is loaded by path (it lives in ``scripts/``). The board, walkthrough and HTML
helpers are torch-free; the model panel is exercised with a ``None`` model.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location(
    "make_process_gallery", ROOT / "scripts" / "make_process_gallery.py"
)
assert _SPEC is not None and _SPEC.loader is not None
pg = importlib.util.module_from_spec(_SPEC)
sys.modules["make_process_gallery"] = pg
_SPEC.loader.exec_module(pg)

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def _demo_data() -> dict:
    report = {
        "ply": 19,
        "fen_before": START_FEN,
        "move_uci": "c3b5",
        "move_san": "Nxb5",
        "quality": {
            "label": "great",
            "eval_after_cp": 446.0,
            "is_only_move": True,
            "is_forcing": True,
        },
        "themes": [{"theme": "sacrifice", "squares": ["b5", "c3"], "pieces": ["N@c3"]}],
        "intent": [{"tag": "attacks_king", "evidence": "x"}],
        "positional_delta": {"material": 100.0, "mobility": 24.0, "space": 0.0},
    }
    explanation = {
        "headline": "Nxb5 — a great move.",
        "sentences": ["It was the only move that keeps the position."],
        "claims": [{"kind": "headline", "text": "Nxb5 — a great move."}],
        "verified": True,
    }
    return {
        "headers": {"White": "Morphy", "Black": "Duke"},
        "game": {"moves": [report]},
        "explanations": [explanation],
    }


def test_board_svg_shades_theme_squares() -> None:
    svg = pg.board_svg(START_FEN, "e2e4", ["d5", "f7"])
    assert svg.startswith("<svg")
    assert "#bcd4ea" in svg  # theme colour
    assert "#f6e58d" in svg  # played-move colour


def test_build_walkthrough_extracts_real_fields() -> None:
    walk = pg.build_walkthrough(_demo_data(), 19)
    assert walk["san"] == "Nxb5"
    assert walk["label"] == "great"
    assert walk["themes"] == ["sacrifice"]
    assert walk["intents"] == ["attacks_king"]
    assert walk["only_move"] and walk["forcing"]
    assert walk["board_svg"].startswith("<svg")
    assert walk["verified"] is True


def test_build_walkthrough_rejects_missing_ply() -> None:
    import pytest

    with pytest.raises(KeyError):
        pg.build_walkthrough(_demo_data(), 3)


def test_figure_tile_embeds_base64_and_caption(tmp_path: Path) -> None:
    png = tmp_path / "chart.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\nFAKE")
    tile = pg.figure_tile(png, "A caption", "scripts/train_model.py")
    assert "data:image/png;base64," in tile
    assert "A caption" in tile
    assert "scripts/train_model.py" in tile


def test_build_html_marks_model_absent_without_checkpoint(tmp_path: Path) -> None:
    png = tmp_path / "chart.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\nFAKE")
    page = pg.build_html([(png, "cap", "script")], pg.build_walkthrough(_demo_data(), 19), None)
    assert page.lstrip().startswith("<!doctype")
    assert "Working process" in page and "Training process" in page
    assert "Nxb5 — a great move." in page
    assert "No checkpoint found" in page
    assert 'href="index.html"' in page and 'href="gallery.html"' in page


def test_model_panel_reports_agreement() -> None:
    model = {
        "quality": [("great", 0.7), ("best", 0.2), ("excellent", 0.1)],
        "themes": ["sacrifice"],
        "intents": [],
    }
    panel = pg._model_panel(model, "great")
    assert "agrees with the rule label" in panel
    differing = pg._model_panel(model, "best")
    assert "differs from the rule label" in differing
