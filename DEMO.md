# DEMO — Verifiable Chess Move Explainer

A three-layer prototype with a visual front door: engine measurement → symbolic rules →
verified explanations, plus a small CNN trained on the rule labels and an image gallery of
how it works and how it trained.

## Start here — one command, nothing to type

**Double-click `run_demo.cmd`** in the repository root. That is the whole demo. It:

1. runs the live pipeline on a real move and prints the verified explanation;
2. writes `demo\live\showcase.json` (report + explanation + claims) and `demo\live\showcase.png`
   (the board with the detected theme squares coloured);
3. opens `demo\index.html` in your browser;
4. pauses so you can read the output.

If you prefer a terminal (or the `.cmd` will not run): one line, no arguments.

```powershell
.\.venv\Scripts\python.exe scripts\demo_run.py
```

Both forms find the engine automatically — no environment setup, no FENs, no flags.

## The pages

| Page | What it shows |
| --- | --- |
| `demo/index.html` | **Overview** — the pipeline concept diagram, the results charts (model vs baseline), and six striking moves with coloured boards. Links to the other two pages. |
| `demo/process.html` | **How it works & how it trained** — a walkthrough of one real move (board → rule report → verified explanation → the model's own head outputs) and the training figures: loss curves, label distribution, per-theme/intent F1, confusion matrix. |
| `demo/gallery.html` | **Move-by-move** — two famous games fully explained, every card with its board, quality badge, grouped claims and an evidence table. |

All three are self-contained (inline SVG and base64 images, no network) and open offline.

## What's already here

| Piece | Where |
| --- | --- |
| Symbolic layer (engine + 40 theme detectors + intent tags) | `src/moveexp/` |
| Explanation layer (facts → render → verify) | `src/moveexp/explain/` |
| Neural baseline (CNN: quality + theme + intent heads) | `src/moveexp/model/` |
| CLI | `moveexp analyze-move` / `explain` / `analyze-pgn` / `batch` / `vocab` |
| Live runner | `scripts/demo_run.py` |
| Training figures | `experiments/figures/` |
| Results numbers | `experiments/model_vs_rules.csv` |
| Tests | `tests/` — run `pytest` (334 passing) |

## One-time setup (already done on this machine)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe scripts\check_env.py   # expect "ALL CHECKS PASSED"
```

Stockfish 19 lives in `tools/` and is found automatically by `scripts/demo_run.py`.

## The 2-minute demo script

1. **Double-click `run_demo.cmd`.** The terminal prints the explanation of Morphy's Nxb5 and
   the paths to the JSON and board PNG. Point out that every line is a *fact* from the report.
2. **In `demo/index.html`:** the pipeline diagram, then the results charts — green is the CNN,
   grey the majority baseline. Themes and intents beat the baseline; quality does not, and the
   caption says why.
3. **Open `demo/process.html`** (linked from the nav): the four-column walkthrough and the
   training figures, including the loss curve that shows the model overfitting a 1571-row
   training set.
4. **Open `demo/gallery.html`:** scroll the Opera Game to move 10 `Nxb5` (sacrifice) and move
   17 `Rd8#` (back-rank mate); blue squares are the detected themes, yellow the played move.
5. **The receipts (optional):** run `moveexp explain --fen "<FEN>" --move Qxf7# --depth 14 --json`
   to show that every sentence carries a `kind`, `evidence` and `source`.

## Regenerate everything

```powershell
.\.venv\Scripts\python.exe scripts\build_demo.py --depth 12          # demo/out/*.md + *.json
.\.venv\Scripts\python.exe scripts\make_gallery.py                   # demo/gallery.html
.\.venv\Scripts\python.exe scripts\make_site.py                      # demo/index.html
.\.venv\Scripts\python.exe scripts\train_model.py --labels data\processed\selfplay.parquet `
    --figures-dir experiments\figures --save experiments\model.pt    # figures + checkpoint
.\.venv\Scripts\python.exe scripts\make_process_gallery.py           # demo/process.html
```

Nothing above needs the network.

## The one-sentence thesis

Engines say *what* is good; this says *why*, and only says what it can prove — the label layer
is rule-based and auditable, the explanation layer refuses to state a fact the report does not
contain, and the model is evaluated honestly against the labels it was trained on.

## Honest limitations (say these if asked)

- **Intent is inferred consequence**, not the player's psychology — a stated design choice.
- **Rules are noisy**: some detectors (`bishop_pair`, `bad_bishop`) fire on almost every move;
  quantifying that with a manual audit is future work.
- **Long-term plans are out of scope** (no "prepares a queenside attack in 10 moves").
- **The model reproduces rule labels, not ground truth**; its baseline is a prior predictor,
  not "the rules". Themes and intents learn above the baseline; move quality does not, on this
  small self-play corpus.
