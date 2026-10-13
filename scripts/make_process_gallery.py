#!/usr/bin/env python3
"""Build ``demo/process.html``: an offline image gallery of the working and training process.

Two halves:

* **Working process** — a walkthrough strip taken from a *real* move in the demo corpus (the
  report and the verified explanation come from the actual pipeline output in
  ``demo/out/*.json``): the board with the detected theme squares coloured, the rule report,
  the verified explanation, and the trained model's own head outputs for the same move.
* **Training process** — the figures written by ``scripts/train_model.py --figures-dir``.

Everything is embedded (images as base64 data URIs, board as inline SVG), so the page opens
fully offline. Run inside the venv::

    .venv\\Scripts\\python.exe scripts/make_process_gallery.py
"""

from __future__ import annotations

import argparse
import base64
import html
import json
from pathlib import Path

import chess
import chess.svg

from moveexp.config import INTENT_VOCAB, PROJECT_ROOT, QUALITY_LABELS, THEME_VOCAB

DEMO_DIR = PROJECT_ROOT / "demo"
OUT_DIR = DEMO_DIR / "out"
FIGURES_DIR = PROJECT_ROOT / "experiments" / "figures"
CHECKPOINT = PROJECT_ROOT / "experiments" / "model.pt"
PAGE = DEMO_DIR / "process.html"

TRAIN_SCRIPT = "scripts/train_model.py --figures-dir experiments/figures"

#: filename -> (caption, producing script)
FIGURE_CAPTIONS: dict[str, tuple[str, str]] = {
    "loss_curves.png": (
        "Training vs validation loss per epoch. Training keeps falling while validation turns "
        "up after roughly epoch 20: the 1571-row training set is overfit, which is why the "
        "trainer keeps the best-validation checkpoint rather than the final weights.",
        TRAIN_SCRIPT,
    ),
    "label_distribution.png": (
        "Move-quality label counts over all 1971 labelled moves. About 83% are "
        "best/excellent/good, which is the root cause of the quality-head result.",
        TRAIN_SCRIPT,
    ),
    "theme_f1.png": ("Per-theme F1 on the held-out games - the head that works.", TRAIN_SCRIPT),
    "intent_f1.png": ("Per-intent F1 on the held-out games.", TRAIN_SCRIPT),
    "quality_confusion.png": (
        "Row-normalised quality confusion matrix on the held-out games.",
        TRAIN_SCRIPT,
    ),
}

_CSS = """
:root { color-scheme: dark; }
* { box-sizing: border-box; }
body { margin: 0; background: #12151b; color: #e7ebf0;
  font: 15px/1.55 -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; }
a { color: #7fb2ff; }
header.top { padding: 30px 32px 24px; border-bottom: 1px solid #262c36; background: #171b23; }
header.top h1 { margin: 0 0 8px; font-size: 24px; }
header.top p { margin: 0 0 14px; color: #9aa6b4; max-width: 900px; }
nav.links a { margin-right: 18px; font-weight: 600; text-decoration: none; }
main { padding: 8px 32px 72px; max-width: 1240px; margin: 0 auto; }
section { margin: 38px 0; }
section > h2 { font-size: 20px; border-left: 3px solid #3f8f5f; padding-left: 10px; }
.strip { display: grid; grid-template-columns: 300px 1.1fr 1.3fr 1.1fr; gap: 14px; align-items: start; }
.col { background: #191e27; border: 1px solid #262c36; border-radius: 10px; padding: 14px; }
.col h3 { margin: 0 0 8px; font-size: 13px; text-transform: uppercase; letter-spacing: .05em; color: #8d99a8; }
.col ul { margin: 6px 0; padding-left: 18px; }
.col li { margin: 2px 0; font-size: 13.5px; }
.board svg { display: block; margin: 0 auto; border-radius: 6px; max-width: 100%; height: auto; }
.badge { display: inline-block; font-size: 11px; text-transform: uppercase; letter-spacing: .04em;
  padding: 2px 8px; border-radius: 999px; font-weight: 700; background: #256b45; color: #dfffe9; }
.chip { display: inline-block; background: #22303f; color: #cfe6ff; border-radius: 999px;
  padding: 1px 8px; font-size: 11.5px; margin: 3px 4px 0 0; }
.chip.m { background: #33304a; color: #ded7ff; }
.hl { font-size: 15px; margin: 0 0 6px; }
.note { color: #9aa6b4; font-size: 12.5px; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(430px, 1fr)); gap: 16px; }
figure.tile { margin: 0; background: #191e27; border: 1px solid #262c36; border-radius: 10px; padding: 12px; }
figure.tile img { width: 100%; height: auto; border-radius: 6px; background: #fff; }
figcaption { color: #cfd6e0; font-size: 13px; margin-top: 8px; }
figcaption .src { display: block; color: #7c8798; font-size: 11.5px; margin-top: 4px; }
code { background: #0e1218; padding: 1px 5px; border-radius: 4px; color: #9ecbff; }
footer { color: #7c8798; font-size: 12.5px; padding: 20px 32px 60px; max-width: 1240px; margin: 0 auto; }
"""


def board_svg(fen: str, uci: str, theme_squares: list[str], size: int = 280) -> str:
    """Inline board SVG: theme squares shaded blue, the played move shaded yellow + arrow."""
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


def build_walkthrough(data: dict, ply: int) -> dict:
    """Assemble the walkthrough payload from a real ``demo/out/*.json`` dump."""
    moves = data["game"]["moves"]
    reports = {int(move["ply"]): move for move in moves}
    if ply not in reports:
        raise KeyError(f"ply {ply} not in {sorted(reports)}")
    report = reports[ply]
    explanation = data["explanations"][moves.index(report)]
    theme_hits = report.get("themes", [])
    squares = sorted({square for hit in theme_hits for square in hit.get("squares", [])})
    return {
        "ply": ply,
        "san": report["move_san"],
        "uci": report["move_uci"],
        "fen": report["fen_before"],
        "label": report["quality"]["label"],
        "eval_after_cp": float(report["quality"]["eval_after_cp"]),
        "only_move": bool(report["quality"]["is_only_move"]),
        "forcing": bool(report["quality"]["is_forcing"]),
        "themes": [hit["theme"] for hit in theme_hits],
        "intents": [tag["tag"] for tag in report.get("intent", [])],
        "delta": report.get("positional_delta", {}),
        "headline": explanation["headline"],
        "sentences": explanation.get("sentences", []),
        "claims": len(explanation.get("claims", [])),
        "verified": bool(explanation.get("verified", False)),
        "board_svg": board_svg(report["fen_before"], report["move_uci"], squares),
        "game": f"{data['headers'].get('White', '?')} vs {data['headers'].get('Black', '?')}",
    }


def model_predictions(checkpoint: Path, fen: str, uci: str) -> dict | None:
    """Run the trained CNN on one move. Returns ``None`` when torch or the checkpoint is absent."""
    try:
        import torch
    except Exception:  # noqa: BLE001 - torch is an optional extra
        return None
    if not checkpoint.exists():
        return None

    from moveexp.model.encode import encode_board
    from moveexp.model.network import MoveNet

    payload = torch.load(checkpoint, map_location="cpu")
    planes = int(payload["in_planes"])
    model = MoveNet(planes, channels=payload["channels"], hidden=payload["hidden"])
    model.load_state_dict(payload["state_dict"])
    model.eval()

    tensor = torch.from_numpy(encode_board(fen, uci)[:planes][None, ...])
    with torch.no_grad():
        quality_logits, theme_logits, intent_logits = model(tensor)
        quality = torch.softmax(quality_logits, dim=1)[0].numpy()
        themes = torch.sigmoid(theme_logits)[0].numpy()
        intents = torch.sigmoid(intent_logits)[0].numpy()

    top = quality.argsort()[::-1][:3]
    return {
        "quality": [(QUALITY_LABELS[int(i)], float(quality[i])) for i in top],
        "themes": [THEME_VOCAB[i] for i in range(len(THEME_VOCAB)) if themes[i] >= 0.5],
        "intents": [INTENT_VOCAB[i] for i in range(len(INTENT_VOCAB)) if intents[i] >= 0.5],
    }


def _embed_png(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def figure_tile(path: Path, caption: str, script: str) -> str:
    """One image tile with a caption and the script that produced it."""
    return (
        '<figure class="tile">'
        f'<img src="{_embed_png(path)}" alt="{html.escape(caption)}">'
        f"<figcaption>{html.escape(caption)}"
        f'<span class="src">produced by <code>{html.escape(script)}</code></span></figcaption>'
        "</figure>"
    )


def _chips(names: list[str], css: str = "chip") -> str:
    if not names:
        return '<span class="note">none</span>'
    return "".join(
        f'<span class="{css}">{html.escape(name.replace("_", " "))}</span>' for name in names
    )


def _model_panel(model: dict | None, rule_label: str) -> str:
    if model is None:
        return (
            '<div class="col"><h3>Model head outputs</h3>'
            '<p class="note">No checkpoint found. Run <code>scripts/train_model.py --save '
            "experiments/model.pt</code> to populate this panel.</p></div>"
        )
    top = model["quality"][0][0] if model["quality"] else "?"
    agrees = top == rule_label
    verdict = "agrees with the rule label" if agrees else "differs from the rule label"
    caveat = (
        ""
        if agrees
        else (
            " Move quality is the head the model does not learn from this corpus (see the "
            "Results page); themes and intents are the heads that do."
        )
    )
    quality = "".join(
        f"<li>{html.escape(name)} <b>{prob:.0%}</b></li>" for name, prob in model["quality"]
    )
    return (
        '<div class="col"><h3>Model head outputs</h3>'
        f'<p class="note">Predicted quality (top 3) &middot; {html.escape(verdict)}.'
        f"{html.escape(caveat)}</p>"
        f"<ul>{quality}</ul>"
        f'<p class="note">Themes</p>{_chips(model["themes"])}'
        f'<p class="note">Intent</p>{_chips(model["intents"], "chip m")}'
        "</div>"
    )


def build_html(figures: list[tuple[Path, str, str]], walkthrough: dict, model: dict | None) -> str:
    """The full self-contained page."""
    tiles = "".join(figure_tile(path, cap, script) for path, cap, script in figures)
    delta = {
        key: value
        for key, value in walkthrough["delta"].items()
        if isinstance(value, int | float) and abs(float(value)) >= 1
    }
    delta_items = "".join(
        f"<li>{html.escape(key.replace('_', ' '))} {float(value):+.1f}</li>"
        for key, value in delta.items()
    )
    flags = []
    if walkthrough["only_move"]:
        flags.append("only move")
    if walkthrough["forcing"]:
        flags.append("forcing")
    flag_text = f" &middot; {', '.join(flags)}" if flags else ""

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>moveexp — how it works and how it trained</title>
<style>{_CSS}</style>
</head>
<body>
<header class="top">
  <h1>How it works, and how it trained</h1>
  <p>The working process on a real move, then the training process behind the model.
  Every image below is a generated artefact; the board and the explanation come from an
  actual pipeline run, not a mock-up. The page is fully offline.</p>
  <nav class="links">
    <a href="index.html">&larr; Overview &amp; results</a>
    <a href="gallery.html">Move-by-move gallery</a>
  </nav>
</header>
<main>
  <section id="working">
    <h2>Working process — one real move, end to end</h2>
    <p class="note">{html.escape(walkthrough["game"])} &middot;
      {walkthrough["ply"] // 2 + 1}{"." if walkthrough["ply"] % 2 == 0 else "..."}
      {html.escape(walkthrough["san"])}{flag_text}</p>
    <div class="strip">
      <div class="col board"><h3>1. Position &amp; themes</h3>{walkthrough["board_svg"]}
        <p class="note">Blue = squares the detected themes refer to; yellow = the played move.</p></div>
      <div class="col"><h3>2. Rule report</h3>
        <p><span class="badge">{html.escape(walkthrough["label"])}</span></p>
        <p class="note">Evaluation {walkthrough["eval_after_cp"] / 100:+.2f} for the mover.</p>
        <p class="note">Themes</p>{_chips(walkthrough["themes"])}
        <p class="note">Intent</p>{_chips(walkthrough["intents"], "chip m")}
        <p class="note">Positional change</p><ul>{delta_items or '<li class="note">none notable</li>'}</ul>
      </div>
      <div class="col"><h3>3. Verified explanation</h3>
        <p class="hl">{html.escape(walkthrough["headline"])}</p>
        <ul>{"".join(f"<li>{html.escape(s)}</li>" for s in walkthrough["sentences"])}</ul>
        <p class="note">{walkthrough["claims"]} claims &middot;
          {"all verified against the report" if walkthrough["verified"] else "SOME UNVERIFIED"}</p>
      </div>
      {_model_panel(model, walkthrough["label"])}
    </div>
  </section>

  <section id="training">
    <h2>Training process</h2>
    <p class="note">Figures from the most recent real training run
      (<code>{html.escape(TRAIN_SCRIPT)}</code>).</p>
    <div class="tiles">{tiles}</div>
  </section>
</main>
<footer>
  Regenerate: <code>scripts/train_model.py --figures-dir experiments/figures --save experiments/model.pt</code>
  then <code>scripts/make_process_gallery.py</code>. Boards are inline SVG and every image is
  embedded, so nothing is loaded from the network.
</footer>
</body>
</html>
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--figures-dir", type=Path, default=FIGURES_DIR)
    parser.add_argument("--demo-json", type=Path, default=OUT_DIR / "opera.json")
    parser.add_argument(
        "--ply",
        type=int,
        default=18,
        help="Which real move to walk through (18 = Morphy's 10.Nxb5 sacrifice).",
    )
    parser.add_argument("--checkpoint", type=Path, default=CHECKPOINT)
    parser.add_argument("--page", type=Path, default=PAGE)
    args = parser.parse_args(argv)

    figure_paths = [
        args.figures_dir / name for name in FIGURE_CAPTIONS if (args.figures_dir / name).exists()
    ]
    if not figure_paths:
        raise SystemExit(
            f"no figures in {args.figures_dir}; run scripts/train_model.py --figures-dir first"
        )
    figures = [(path, *FIGURE_CAPTIONS[path.name]) for path in figure_paths]

    if not args.demo_json.exists():
        raise SystemExit(f"no demo JSON at {args.demo_json}; run scripts/build_demo.py first")
    data = json.loads(args.demo_json.read_text(encoding="utf-8"))
    walkthrough = build_walkthrough(data, args.ply)
    model = model_predictions(args.checkpoint, walkthrough["fen"], walkthrough["uci"])

    args.page.write_text(build_html(figures, walkthrough, model), encoding="utf-8")
    size_kib = args.page.stat().st_size // 1024
    print(
        f"wrote {args.page} ({size_kib} KiB, {len(figures)} figures, "
        f"model panel {'on' if model else 'off'})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
