#!/usr/bin/env python3
"""Render every ``demo/out/*.json`` into a single self-contained ``demo/gallery.html``.

The gallery is the demo artefact: one card per move, with the board shown before the
move (the played move highlighted by an arrow), the quality badge, the verified
headline, the claims grouped by kind, and a collapsible table proving each sentence's
evidence. Nothing is fetched at view time - boards are inlined SVG, styles are inlined
CSS - so the file opens offline in any browser.

Run inside the venv::

    .venv\\Scripts\\python.exe scripts/make_gallery.py
"""

from __future__ import annotations

import argparse
import html
import json
from collections.abc import Iterable
from pathlib import Path

import chess
import chess.svg

from moveexp.config import PROJECT_ROOT

DEMO_DIR = PROJECT_ROOT / "demo"
OUT_DIR = DEMO_DIR / "out"
GALLERY_PATH = DEMO_DIR / "gallery.html"

_KIND_TITLES = {
    "evaluation": "Verdict",
    "criticality": "Criticality",
    "theme": "Tactics & themes",
    "positional": "Positional change",
    "intent": "Likely intent",
    "engine": "Engine",
}
_KIND_ORDER = ("evaluation", "criticality", "theme", "positional", "intent", "engine")

_CSS = """
:root { color-scheme: dark; }
* { box-sizing: border-box; }
body { margin: 0; background: #12151b; color: #e7ebf0;
  font: 15px/1.5 -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; }
header.top { padding: 28px 32px; border-bottom: 1px solid #262c36; background: #171b23; }
header.top h1 { margin: 0 0 6px; font-size: 22px; }
header.top p { margin: 0; color: #9aa6b4; }
main { padding: 24px 32px 64px; max-width: 1280px; margin: 0 auto; }
section.game { margin-bottom: 48px; }
section.game > h2 { font-size: 19px; border-left: 3px solid #3f8f5f; padding-left: 10px; }
section.game > p.sub { color: #9aa6b4; margin: 4px 0 20px; }
.moves { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 18px; }
article.move { background: #191e27; border: 1px solid #262c36; border-radius: 10px;
  padding: 14px; display: flex; flex-direction: column; gap: 12px; }
.board { display: flex; justify-content: center; }
.board svg { border-radius: 6px; max-width: 100%; height: auto; }
.head { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.num { color: #7c8798; font-variant-numeric: tabular-nums; }
.san { font-weight: 700; font-size: 16px; }
.badge { font-size: 11px; text-transform: uppercase; letter-spacing: .04em;
  padding: 2px 8px; border-radius: 999px; font-weight: 700; }
.b-brilliant,.b-great { background: #2b6f8f; color: #dff2ff; }
.b-best { background: #256b45; color: #dfffe9; }
.b-excellent { background: #2f6b56; color: #e0fff2; }
.b-good { background: #3a4657; color: #dfe7f2; }
.b-inaccuracy { background: #7a6320; color: #fff6d9; }
.b-mistake { background: #8a5320; color: #ffe9d2; }
.b-blunder { background: #8a2f2f; color: #ffdede; }
.hl { margin: 0; font-size: 15px; }
.verified { font-size: 11px; color: #74c69d; }
.verified.bad { color: #e76f51; }
.grp h4 { margin: 10px 0 4px; font-size: 11px; text-transform: uppercase;
  letter-spacing: .05em; color: #8d99a8; }
.grp ul { margin: 0; padding-left: 18px; }
.grp li { margin: 2px 0; color: #cfd6e0; }
details { margin-top: 8px; }
summary { cursor: pointer; color: #8d99a8; font-size: 12px; }
table { width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 12px; }
th, td { text-align: left; padding: 4px 6px; border-bottom: 1px solid #262c36; vertical-align: top; }
th { color: #8d99a8; font-weight: 600; }
code { background: #0e1218; padding: 1px 5px; border-radius: 4px; color: #9ecbff; }
"""


def board_svg(
    fen: str,
    uci: str,
    size: int = 300,
    theme_squares: Iterable[str] = (),
) -> str:
    """Inline SVG of ``fen`` with the played move and detected theme squares highlighted.

    Theme squares are shaded pale blue; the played move's from/to squares are shaded
    yellow and an arrow marks the move, so the tactics the detectors found are literally
    visible on the board.
    """
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


def _group_claims(explanation: dict) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for claim in explanation.get("claims", []):
        grouped.setdefault(claim["kind"], []).append(claim)
    return grouped


def move_card(report: dict, explanation: dict, size: int = 300) -> str:
    """One move: board, badge, headline, grouped claims, and an evidence table."""
    label = report["quality"]["label"]
    ply = int(report["ply"])
    number = ply // 2 + 1
    dots = "." if ply % 2 == 0 else "..."
    theme_squares = sorted(
        {square for hit in report.get("themes", []) for square in hit.get("squares", [])}
    )
    svg = board_svg(report["fen_before"], report["move_uci"], size, theme_squares)

    grouped = _group_claims(explanation)
    blocks = []
    for kind in _KIND_ORDER:
        items = grouped.get(kind)
        if not items:
            continue
        rows = "".join(
            f'<li title="{html.escape(claim.get("evidence", ""))}">'
            f"{html.escape(claim['text'])}</li>"
            for claim in items
        )
        blocks.append(
            f'<div class="grp"><h4>{html.escape(_KIND_TITLES[kind])}</h4><ul>{rows}</ul></div>'
        )

    claims = explanation.get("claims", [])
    verified = explanation.get("verified", False)
    badge = "verified" if verified else "bad"
    verified_text = f"{len(claims)} claims · {'all verified' if verified else 'SOME UNVERIFIED'}"
    table_rows = "".join(
        f"<tr><td><code>{html.escape(c['kind'])}</code></td>"
        f"<td>{html.escape(c['text'])}</td>"
        f"<td>{html.escape(c.get('evidence', ''))}</td></tr>"
        for c in claims
    )

    return f"""<article class="move">
  <div class="board">{svg}</div>
  <div class="head">
    <span class="num">{number}{dots}</span>
    <span class="san">{html.escape(report["move_san"])}</span>
    <span class="badge b-{html.escape(label)}">{html.escape(label)}</span>
    <span class="verified {badge}">{verified_text}</span>
  </div>
  <p class="hl">{html.escape(explanation["headline"])}</p>
  {"".join(blocks)}
  <details><summary>evidence table</summary>
    <table><thead><tr><th>kind</th><th>claim</th><th>evidence</th></tr></thead>
    <tbody>{table_rows}</tbody></table>
  </details>
</article>"""


def build_game_section(stem: str, data: dict, size: int = 300) -> str:
    """A whole game: heading plus one card per move."""
    headers = data.get("headers", {})
    game = data.get("game", {})
    players = game.get("players", {})
    white = headers.get("White") or players.get("white") or "?"
    black = headers.get("Black") or players.get("black") or "?"
    result = headers.get("Result") or game.get("result") or "*"
    subtitle = " · ".join(str(x) for x in (headers.get("Event"), headers.get("Date"), result) if x)

    cards = "".join(
        move_card(report, explanation, size)
        for report, explanation in zip(
            game.get("moves", []), data.get("explanations", []), strict=False
        )
    )
    anchor = html.escape(stem)
    return f"""<section class="game" id="{anchor}">
  <h2>{html.escape(white)} vs {html.escape(black)}</h2>
  <p class="sub">{html.escape(subtitle)}</p>
  <div class="moves">{cards}</div>
</section>"""


def build_html(games: list[tuple[str, dict]], size: int = 300) -> str:
    """The full self-contained gallery page for ``[(stem, data), ...]``."""
    total_moves = sum(len(d.get("explanations", [])) for _, d in games)
    total_claims = sum(
        len(e.get("claims", [])) for _, d in games for e in d.get("explanations", [])
    )
    sections = "".join(build_game_section(stem, data, size) for stem, data in games)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>moveexp — verified move explanations</title>
<style>{_CSS}</style>
</head>
<body>
<header class="top">
  <h1>Verified chess move explanations</h1>
  <p>{len(games)} game(s) · {total_moves} moves · {total_claims} claims,
     every sentence checked against its engine-backed report.</p>
</header>
<main>
{sections}
</main>
</body>
</html>
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--gallery", type=Path, default=GALLERY_PATH)
    parser.add_argument("--size", type=int, default=300, help="Board SVG size in pixels.")
    args = parser.parse_args(argv)

    paths = sorted(args.out_dir.glob("*.json"))
    if not paths:
        raise SystemExit(f"no demo JSON in {args.out_dir}; run scripts/build_demo.py first")

    games = [(path.stem, json.loads(path.read_text(encoding="utf-8"))) for path in paths]
    args.gallery.write_text(build_html(games, size=args.size), encoding="utf-8")
    print(f"wrote {args.gallery} ({args.gallery.stat().st_size // 1024} KiB, {len(games)} games)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
