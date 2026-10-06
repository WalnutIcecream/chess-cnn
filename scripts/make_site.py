#!/usr/bin/env python3
"""Build ``demo/index.html``: the visual landing page for the demo.

Three things a supervisor can look at in a live room:

* **Concept** — a one-glance pipeline diagram (engine -> rules -> weak labels -> CNN ->
  verified explanation) and one-line definitions of each label family.
* **Results** — real numbers from ``experiments/model_vs_rules.csv`` drawn as bar charts
  (model vs majority baseline), not buried in prose.
* **Highlights** — the most striking moves from the demo games, with the detected theme
  squares coloured on the board, linking through to the full move-by-move gallery.

Self-contained: inline CSS/SVG, no CDN, opens offline. Run inside the venv::

    .venv\\Scripts\\python.exe scripts/make_site.py
"""

from __future__ import annotations

import argparse
import csv
import html
import json
from pathlib import Path

import chess
import chess.svg

from moveexp.config import PROJECT_ROOT

DEMO_DIR = PROJECT_ROOT / "demo"
OUT_DIR = DEMO_DIR / "out"
RESULTS_CSV = PROJECT_ROOT / "experiments" / "model_vs_rules.csv"
SITE_PATH = DEMO_DIR / "index.html"

#: Themes that make a move worth showing on the landing page.
NOTABLE_THEMES = (
    "back_rank_mate",
    "sacrifice",
    "fork",
    "pin",
    "skewer",
    "discovered_check",
    "double_check",
    "promotion",
)
#: Quality labels that make a move worth showing.
NOTABLE_LABELS = ("brilliant", "great")

_MODEL_COLOR = "#3f8f5f"
_BASE_COLOR = "#8d99a8"

_CSS = """
:root { color-scheme: dark; }
* { box-sizing: border-box; }
body { margin: 0; background: #12151b; color: #e7ebf0;
  font: 15px/1.55 -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; }
a { color: #7fb2ff; }
header.top { padding: 34px 32px 26px; border-bottom: 1px solid #262c36; background: #171b23; }
header.top h1 { margin: 0 0 8px; font-size: 26px; }
header.top p.lede { margin: 0 0 16px; color: #9aa6b4; max-width: 900px; }
nav.links a { margin-right: 18px; font-weight: 600; text-decoration: none; }
main { padding: 8px 32px 72px; max-width: 1180px; margin: 0 auto; }
section { margin: 40px 0; }
section > h2 { font-size: 20px; border-left: 3px solid #3f8f5f; padding-left: 10px; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; }
.card { background: #191e27; border: 1px solid #262c36; border-radius: 10px; padding: 14px; }
.card h3 { margin: 0 0 6px; font-size: 15px; }
.card p { margin: 0; color: #cfd6e0; font-size: 13.5px; }
.charts { display: grid; grid-template-columns: repeat(auto-fit, minmax(430px, 1fr)); gap: 18px; }
.chart { background: #191e27; border: 1px solid #262c36; border-radius: 10px; padding: 16px; }
.chart h3 { margin: 0 0 10px; font-size: 15px; text-transform: capitalize; }
.cl { fill: #cfd6e0; font-size: 12.5px; }
.cv { fill: #9aa6b4; font-size: 11.5px; }
.legend { color: #9aa6b4; font-size: 12.5px; margin: 4px 0 14px; }
.swatch { display: inline-block; width: 11px; height: 11px; border-radius: 3px; vertical-align: -1px; margin: 0 5px 0 12px; }
.hl-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; }
.hl { background: #191e27; border: 1px solid #262c36; border-radius: 10px; padding: 12px; }
.hl .board svg { display: block; margin: 0 auto; border-radius: 6px; max-width: 100%; height: auto; }
.hl .meta { margin-top: 8px; font-size: 13px; }
.hl .game { color: #8d99a8; font-size: 12px; }
.tags span { display: inline-block; background: #22303f; color: #cfe6ff; border-radius: 999px;
  padding: 1px 8px; font-size: 11px; margin: 4px 4px 0 0; }
table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12.5px; }
th, td { text-align: left; padding: 5px 8px; border-bottom: 1px solid #262c36; }
th { color: #8d99a8; }
.note { color: #9aa6b4; font-size: 13px; }
footer { color: #7c8798; font-size: 12.5px; padding: 20px 32px 60px; max-width: 1180px; margin: 0 auto; }
"""


def board_svg(fen: str, uci: str, theme_squares: list[str], size: int = 260) -> str:
    """Inline board SVG with theme squares shaded blue and the move shaded yellow."""
    board = chess.Board(fen)
    fill: dict[chess.Square, str] = {}
    for name in theme_squares:
        try:
            fill[chess.parse_square(name)] = "#bcd4ea"
        except ValueError:
            continue
    arrows: list[chess.svg.Arrow] = []
    try:
        move = chess.Move.from_uci(uci)
    except ValueError:
        move = None
    if move is not None:
        arrows = [chess.svg.Arrow(move.from_square, move.to_square, color="#2b7a4b")]
        fill[move.from_square] = "#f6e58d"
        fill[move.to_square] = "#f6e58d"
    return chess.svg.board(board, size=size, arrows=arrows, fill=fill)


def concept_diagram(steps: list[str], width: int = 1020, height: int = 132) -> str:
    """A left-to-right pipeline diagram: evenly spaced boxes joined by arrows."""
    n = len(steps)
    margin = 16
    box_w = (width - 2 * margin - (n - 1) * 26) / n
    box_h = 62
    top = (height - box_h) / 2 - 8
    parts = [f'<svg viewBox="0 0 {width} {height}" width="100%" role="img" aria-label="pipeline">']
    for index, label in enumerate(steps):
        x = margin + index * (box_w + 26)
        parts.append(
            f'<rect x="{x:.1f}" y="{top:.1f}" width="{box_w:.1f}" height="{box_h}" rx="9" '
            f'fill="#1f2733" stroke="#33415a"/>'
        )
        lines = label.split("\n")
        for line_index, line in enumerate(lines):
            y = top + box_h / 2 - (len(lines) - 1) * 8 + line_index * 16 + 4
            weight = "700" if line_index == 0 else "400"
            fill = "#e7ebf0" if line_index == 0 else "#9aa6b4"
            parts.append(
                f'<text x="{x + box_w / 2:.1f}" y="{y:.1f}" text-anchor="middle" '
                f'fill="{fill}" font-size="12.5" font-weight="{weight}">{html.escape(line)}</text>'
            )
        if index < n - 1:
            ax = x + box_w + 5
            parts.append(
                f'<path d="M{ax:.1f} {top + box_h / 2:.1f} l12 0" stroke="#3f8f5f" '
                f'stroke-width="2"/><path d="M{ax + 12:.1f} {top + box_h / 2:.1f} l-5 -4 '
                f'l0 8 z" fill="#3f8f5f"/>'
            )
    parts.append("</svg>")
    return "".join(parts)


def bar_chart(entries: list[tuple[str, float, float]], width: int = 540) -> str:
    """Horizontal grouped bars: ``(label, model, baseline)`` per row, scaled 0..1."""
    label_w = 132
    pad = 12
    row_h = 42
    bar_h = 13
    track = width - label_w - 62
    height = pad * 2 + row_h * len(entries)
    parts = [f'<svg viewBox="0 0 {width} {height}" width="100%" role="img">']
    for index, (label, model, baseline) in enumerate(entries):
        y = pad + index * row_h
        parts.append(f'<text x="{pad}" y="{y + 15:.1f}" class="cl">{html.escape(label)}</text>')
        for offset, value, color in ((0, model, _MODEL_COLOR), (bar_h + 4, baseline, _BASE_COLOR)):
            w = max(0.0, min(1.0, value)) * track
            by = y + 2 + offset
            parts.append(
                f'<rect x="{label_w}" y="{by:.1f}" width="{w:.1f}" height="{bar_h}" rx="3" '
                f'fill="{color}"/>'
            )
            parts.append(
                f'<text x="{label_w + w + 6:.1f}" y="{by + bar_h - 2:.1f}" class="cv">'
                f"{value:.3f}</text>"
            )
    parts.append("</svg>")
    return "".join(parts)


def load_results(path: Path, variant: str) -> dict[str, list[tuple[str, float, float]]]:
    """Group CSV rows into ``{head: [(metric, model, baseline), ...]}`` for one variant."""
    grouped: dict[str, list[tuple[str, float, float]]] = {}
    with path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["variant"] != variant:
                continue
            grouped.setdefault(row["head"], []).append(
                (row["metric"], float(row["model"]), float(row["majority_baseline"]))
            )
    return grouped


def select_highlights(
    games: list[tuple[str, dict]], limit: int = 6
) -> list[tuple[str, dict, dict, list[str]]]:
    """Pick the most striking moves across the games (one per game first, then fill)."""
    scored: list[tuple[int, str, dict, dict, list[str]]] = []
    for stem, data in games:
        for report, explanation in zip(
            data.get("game", {}).get("moves", []), data.get("explanations", []), strict=False
        ):
            themes = [hit["theme"] for hit in report.get("themes", [])]
            score = sum(3 for theme in themes if theme in NOTABLE_THEMES)
            if report["quality"]["label"] in NOTABLE_LABELS:
                score += 3
            if score:
                scored.append((score, stem, report, explanation, themes))
    scored.sort(key=lambda item: item[0], reverse=True)

    picked: list[tuple[str, dict, dict, list[str]]] = []
    seen_games: set[str] = set()
    for _score, stem, report, explanation, themes in scored:
        if stem in seen_games:
            continue
        seen_games.add(stem)
        picked.append((stem, report, explanation, themes))
        if len(picked) >= limit:
            return picked
    for _score, stem, report, explanation, themes in scored:
        if len(picked) >= limit:
            break
        picked.append((stem, report, explanation, themes))
    return picked


def _highlight_card(item: tuple[str, dict, dict, list[str]], data_by_stem: dict[str, dict]) -> str:
    stem, report, explanation, themes = item
    headers = data_by_stem[stem].get("headers", {})
    game = f"{headers.get('White', '?')} vs {headers.get('Black', '?')}"
    ply = int(report["ply"])
    number = ply // 2 + 1
    dots = "." if ply % 2 == 0 else "..."
    squares = sorted({s for hit in report.get("themes", []) for s in hit.get("squares", [])})
    svg = board_svg(report["fen_before"], report["move_uci"], squares)
    tags = "".join(f"<span>{html.escape(t.replace('_', ' '))}</span>" for t in themes[:8])
    return f"""<article class="hl">
  <div class="board">{svg}</div>
  <div class="meta">
    <div class="game">{html.escape(game)} · {number}{dots} {html.escape(report["move_san"])}
      · <b>{html.escape(report["quality"]["label"])}</b></div>
    <div>{html.escape(explanation["headline"])}</div>
    <div class="tags">{tags}</div>
  </div>
</article>"""


def build_html(
    games: list[tuple[str, dict]],
    results: dict[str, list[tuple[str, float, float]]],
    variant: str,
    highlight_limit: int = 6,
) -> str:
    data_by_stem = dict(games)
    steps = [
        "Stockfish engine\nobjective numbers",
        "Symbolic rules\n40 themes + intents",
        "Weak labels\nauto + checkable",
        "CNN\nboard -> labels",
        "Verified explanation\nfacts only",
    ]
    concept_cards = [
        (
            "Quality",
            "How much the move cost or gained, from win-probability loss "
            "(best / excellent / good / inaccuracy / mistake / blunder, plus "
            "brilliant and great when a sacrifice is engine-confirmed).",
        ),
        (
            "Tactical themes",
            "40 hand-written detectors over the board geometry: fork, pin, "
            "skewer, discovered attack, back-rank mate, sacrifice, passed "
            "pawn, outpost, ...",
        ),
        (
            "Intent tags",
            "Inferred consequence, not psychology: develops, castles, "
            "attacks_king, restricts_opponent, trades_defender, ...",
        ),
        (
            "Verification",
            "Every explanation sentence is re-derived from the engine-backed "
            "report; anything the report does not support is dropped, not printed.",
        ),
    ]
    charts = []
    for head in ("quality", "theme", "intent"):
        entries = results.get(head)
        if not entries:
            continue
        charts.append(f'<div class="chart"><h3>{html.escape(head)}</h3>{bar_chart(entries)}</div>')
    chart_html = "".join(charts) or '<p class="note">No results CSV found — run train_model.py.</p>'

    table_rows = "".join(
        f"<tr><td>{html.escape(head)}</td><td>{html.escape(metric)}</td>"
        f"<td>{model:.3f}</td><td>{baseline:.3f}</td></tr>"
        for head, entries in results.items()
        for metric, model, baseline in entries
    )

    highlights = select_highlights(games, limit=highlight_limit)
    highlight_html = "".join(_highlight_card(item, data_by_stem) for item in highlights)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>moveexp — explainable chess move analysis</title>
<style>{_CSS}</style>
</head>
<body>
<header class="top">
  <h1>Explaining the <em>intent</em> behind chess moves</h1>
  <p class="lede">Stockfish says <em>what</em> is good; this says <em>why</em> — and only
  says what it can prove. Symbolic rules over the board produce checkable labels; a small
  CNN learns to predict them from the board alone; an explanation layer writes prose that
  is verified against the engine-backed report.</p>
  <nav class="links">
    <a href="#concept">Concept</a>
    <a href="#results">Results</a>
    <a href="#highlights">Highlights</a>
    <a href="gallery.html">Full move-by-move gallery →</a>
  </nav>
</header>
<main>
  <section id="concept">
    <h2>How it works</h2>
    {concept_diagram(steps)}
    <div class="cards" style="margin-top:18px">
      {"".join(f'<div class="card"><h3>{html.escape(t)}</h3><p>{html.escape(d)}</p></div>' for t, d in concept_cards)}
    </div>
  </section>

  <section id="results">
    <h2>Results — does the model learn the labels from the board alone?</h2>
    <p class="legend">
      <span class="swatch" style="background:{_MODEL_COLOR}"></span>CNN model
      <span class="swatch" style="background:{_BASE_COLOR}"></span>majority / prior baseline
      · variant <b>{html.escape(variant)}</b>, held-out games
    </p>
    <div class="charts">{chart_html}</div>
    <table>
      <thead><tr><th>head</th><th>metric</th><th>model</th><th>baseline</th></tr></thead>
      <tbody>{table_rows}</tbody>
    </table>
    <p class="note">Themes and intents are learnable from the board; move quality is not on
    this small self-play corpus (83% of labels are best/excellent/good). The baseline is a
    prior predictor, <em>not</em> "the rules" — the rules generated the labels, so this
    measures learnability, not correctness.</p>
  </section>

  <section id="highlights">
    <h2>Highlights — the tactics, made visible</h2>
    <p class="note">Detected theme squares are shaded blue; the played move is shaded yellow
    with an arrow. Every caption is verified against the report.</p>
    <div class="hl-grid">{highlight_html}</div>
    <p class="note" style="margin-top:16px">
      <a href="gallery.html">Open the full move-by-move gallery (every move, every claim) →</a>
    </p>
  </section>
</main>
<footer>
  Regenerate: <code>.venv\\Scripts\\python.exe scripts/make_site.py</code> ·
  boards are inline SVG, nothing is loaded from the network.
</footer>
</body>
</html>
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--results", type=Path, default=RESULTS_CSV)
    parser.add_argument("--variant", default="with_move")
    parser.add_argument("--highlights", type=int, default=6)
    parser.add_argument("--site", type=Path, default=SITE_PATH)
    args = parser.parse_args(argv)

    paths = sorted(args.out_dir.glob("*.json"))
    if not paths:
        raise SystemExit(f"no demo JSON in {args.out_dir}; run scripts/build_demo.py first")
    games = [(path.stem, json.loads(path.read_text(encoding="utf-8"))) for path in paths]
    results = load_results(args.results, args.variant) if args.results.exists() else {}

    args.site.write_text(
        build_html(games, results, args.variant, args.highlights), encoding="utf-8"
    )
    size_kib = args.site.stat().st_size // 1024
    print(f"wrote {args.site} ({size_kib} KiB, {len(games)} games, {len(results)} heads)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
