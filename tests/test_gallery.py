"""Tests for the demo gallery builder.

The builder lives in ``scripts/`` outside the package, so it is loaded by path here, the
same way ``test_puzzle_benchmark`` loads the ``eval/`` script.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location("make_gallery", ROOT / "scripts" / "make_gallery.py")
assert _SPEC is not None and _SPEC.loader is not None
gal = importlib.util.module_from_spec(_SPEC)
sys.modules["make_gallery"] = gal
_SPEC.loader.exec_module(gal)

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def _explanation() -> dict:
    return {
        "ply": 0,
        "move_san": "e4",
        "move_uci": "e2e4",
        "headline": "e4 — the best move.",
        "sentences": ["The evaluation remains +0.30 for the mover."],
        "claims": [
            {
                "kind": "headline",
                "text": "e4 — the best move.",
                "evidence": "quality.label=best",
                "source": {},
            },
            {
                "kind": "evaluation",
                "text": "The evaluation remains +0.30 for the mover.",
                "evidence": "eval_after_cp=30",
                "source": {},
            },
            {
                "kind": "theme",
                "text": "Controls center: central control rises.",
                "evidence": "centre squares",
                "source": {},
            },
        ],
        "unverified": [],
        "verified": True,
    }


def _data() -> dict:
    return {
        "headers": {
            "White": "A",
            "Black": "B",
            "Event": "Test",
            "Date": "2020",
            "Result": "1-0",
        },
        "game": {
            "players": {"white": "A", "black": "B"},
            "result": "1-0",
            "moves": [
                {
                    "ply": 0,
                    "move_san": "e4",
                    "move_uci": "e2e4",
                    "fen_before": START_FEN,
                    "quality": {"label": "best"},
                }
            ],
        },
        "explanations": [_explanation()],
    }


def test_board_svg_is_inline_svg_with_highlight() -> None:
    svg = gal.board_svg(START_FEN, "e2e4")
    assert svg.startswith("<svg")
    assert "#f6e58d" in svg


def test_board_svg_shades_theme_squares() -> None:
    svg = gal.board_svg(START_FEN, "e2e4", theme_squares=["d5", "f7"])
    assert "#bcd4ea" in svg  # theme-square colour
    assert "#f6e58d" in svg  # played-move colour still present


def test_board_svg_ignores_bad_square_names() -> None:
    assert gal.board_svg(START_FEN, "e2e4", theme_squares=["not-a-square"]).startswith("<svg")


def test_build_html_is_self_contained_and_escaped() -> None:
    page = gal.build_html([("demo", _data())])
    assert page.lstrip().startswith("<!doctype")
    assert "e4 — the best move." in page
    assert page.count("<article") == 1
    assert "Tactics &amp; themes" in page
    assert "UNVERIFIED" not in page


def test_game_section_uses_headers_for_the_title() -> None:
    section = gal.build_game_section("demo", _data())
    assert "A vs B" in section
    assert "Test · 2020 · 1-0" in section
