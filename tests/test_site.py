"""Tests for the demo landing-page builder (``scripts/make_site.py``)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location("make_site", ROOT / "scripts" / "make_site.py")
assert _SPEC is not None and _SPEC.loader is not None
site = importlib.util.module_from_spec(_SPEC)
sys.modules["make_site"] = site
_SPEC.loader.exec_module(site)

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def _game(stem: str, label: str, theme: str) -> tuple[str, dict]:
    report = {
        "ply": 6,
        "move_san": "Qxf7#",
        "move_uci": "f3f7",
        "fen_before": START_FEN,
        "quality": {"label": label},
        "themes": [{"theme": theme, "squares": ["f7", "e8"]}],
    }
    explanation = {"headline": "Qxf7# — a great move.", "claims": [], "verified": True}
    data = {
        "headers": {"White": "A", "Black": "B"},
        "game": {"moves": [report]},
        "explanations": [explanation],
    }
    return (stem, data)


def test_load_results_groups_by_head(tmp_path: Path) -> None:
    csv_path = tmp_path / "r.csv"
    csv_path.write_text(
        "variant,head,metric,model,majority_baseline\n"
        "with_move,quality,accuracy,0.2,0.445\n"
        "with_move,theme,macro_f1,0.22,0.02\n"
        "without_move,quality,accuracy,0.1,0.445\n",
        encoding="utf-8",
    )
    grouped = site.load_results(csv_path, "with_move")
    assert set(grouped) == {"quality", "theme"}
    assert grouped["quality"] == [("accuracy", 0.2, 0.445)]
    assert grouped["theme"] == [("macro_f1", 0.22, 0.02)]


def test_bar_chart_is_svg_with_values() -> None:
    svg = site.bar_chart([("accuracy", 0.2, 0.445)])
    assert svg.startswith("<svg")
    assert site._MODEL_COLOR in svg and site._BASE_COLOR in svg
    assert "0.200" in svg and "0.445" in svg


def test_concept_diagram_contains_every_step() -> None:
    svg = site.concept_diagram(["Engine\nnumbers", "Rules\nthemes"])
    assert svg.startswith("<svg")
    assert "Engine" in svg and "Rules" in svg


def test_select_highlights_prefers_one_per_game() -> None:
    games = [_game("g1", "great", "back_rank_mate"), _game("g2", "best", "fork")]
    picks = site.select_highlights(games, limit=2)
    assert {stem for stem, *_ in picks} == {"g1", "g2"}


def test_build_html_has_sections_and_gallery_link() -> None:
    games = [_game("g1", "great", "back_rank_mate")]
    page = site.build_html(games, {"theme": [("macro_f1", 0.22, 0.02)]}, "with_move")
    assert page.lstrip().startswith("<!doctype")
    assert 'id="concept"' in page and 'id="results"' in page and 'id="highlights"' in page
    assert "gallery.html" in page
    assert "Qxf7#" in page


def test_highlight_card_escapes_and_shades() -> None:
    stem, data = _game("g1", "great", "fork")
    report = data["game"]["moves"][0]
    card = site._highlight_card((stem, report, data["explanations"][0], ["fork"]), {stem: data})
    assert "#bcd4ea" in card  # theme squares shaded
    assert "fork" in card
