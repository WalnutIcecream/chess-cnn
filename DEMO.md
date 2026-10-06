# DEMO — Verifiable Chess Move Explainer

A three-layer prototype with a visual front door. A played move goes in; an engine-backed
report comes out; an explanation layer writes prose in which **every sentence is verified
against the report** (anything unsupported is dropped, not printed); and a small CNN shows
the labels are learnable from the board alone.

**Start the demo here:** open `demo\index.html` — one page with the concept, the results
charts, and the striking moves. It links to `demo\gallery.html` for the full move-by-move
view.

## What's already here

| Piece | Where |
| --- | --- |
| Symbolic layer (engine + 40 theme detectors + intent tags) | `src/moveexp/` |
| Explanation layer (facts -> render -> verify) | `src/moveexp/explain/` |
| Neural baseline (CNN: quality + theme + intent heads) | `src/moveexp/model/` |
| CLI | `moveexp analyze-move` / `explain` / `analyze-pgn` / `batch` / `vocab` |
| **Landing page (concept + results + highlights)** | `demo/index.html` |
| **Full move-by-move gallery** | `demo/gallery.html` |
| Results numbers | `experiments/model_vs_rules.csv` |
| Tests | `tests/` (310+ passing; run `pytest`) |

## One-time setup (already done on this machine)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
$env:STOCKFISH_PATH = "C:\Users\Walnut Icecream\Documents\chess-cnn\tools\stockfish\stockfish\stockfish-windows-x86-64-universal.exe"
.\.venv\Scripts\python.exe scripts\check_env.py   # expect "ALL CHECKS PASSED"
```

## The 2-minute demo script

**1. The landing page (45 s).** The concept, the numbers, and the tactics in one screen:

```powershell
start demo\index.html
```

- **How it works**: engine -> symbolic rules -> weak labels -> CNN -> verified explanation.
- **Results**: three charts (quality / theme / intent) — green = CNN, grey = majority
  baseline. Point at the theme chart: the model clearly beats the baseline; point at the
  quality chart: it does not, and say why (83% of moves are best/excellent/good).
- **Highlights**: six striking moves with the detected theme squares in blue and the played
  move in yellow. Every caption is a verified claim.

**2. The gallery (45 s).** Every move of two famous games, explained:

```powershell
start demo\gallery.html
```

Each card: the board before the move (theme squares blue, move yellow), the quality badge,
the verified headline, claims grouped by kind, and an **evidence table** mapping each
sentence to the report field behind it. Land on Morphy's Opera Game move 10. `Nxb5`
(sacrifice) and move 17. `Rd8#` (back-rank mate).

**3. The receipts (20 s).** One move, straight from the terminal, as structured data:

```powershell
.\.venv\Scripts\moveexp.exe explain `
  --fen "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 4 4" `
  --move "Qxf7#" --depth 14 --json
```

Every claim carries `kind`, `text`, `evidence` and `source`; `"verified": true` means each
sentence was re-derived from the report. Drop `--json` for the plain-English version.

## Regenerate everything

```powershell
.\.venv\Scripts\python.exe scripts\build_demo.py --depth 12   # demo/out/*.md + *.json
.\.venv\Scripts\python.exe scripts\make_gallery.py            # demo/gallery.html
.\.venv\Scripts\python.exe scripts\make_site.py               # demo/index.html
```

The neural numbers come from `scripts/generate_games.py` (self-play corpus, no downloads)
then `scripts/train_model.py`. Nothing above needs the network.

## The one-sentence thesis

Engines say *what* is good; this says *why*, and only says what it can prove — the label
layer is rule-based and auditable, the explanation layer refuses to state a fact the report
does not contain, and the model is evaluated honestly against the labels it was trained on.

## Honest limitations (say these if asked)

- **Intent is inferred consequence**, not the player's psychology — a stated design choice.
- **Rules are noisy**: some detectors (`bishop_pair`, `bad_bishop`) fire on almost every
  move; quantifying that with a manual audit is future work.
- **Long-term plans are out of scope** (no "prepares a queenside attack in 10 moves").
- **The model reproduces rule labels, not ground truth**; its baseline is a prior
  predictor, not "the rules". Themes/intents learn above the baseline; move quality does
  not, on this small self-play corpus.
