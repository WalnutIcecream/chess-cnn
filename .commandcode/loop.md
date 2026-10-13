# moveexp — demo & presentation build

The system is technically complete (PROGRESS §11–14: symbolic layer, verified explanation
layer, visual landing page, neural baseline, PBL report). This loop makes it **showable**: a
real runnable output, and an image gallery of the working process.

## Focus (required)

1. **Real output the presenter can run live.** A command that takes something supplied on the
   spot — a PGN file, or a FEN + move — and produces a genuine result then and there: the
   verified explanation on the terminal, the structured JSON, and a rendered board image.
   No canned text, no pre-recorded output.
2. **An image gallery of the working process.** A page that shows *how it works and how it
   trained*, not only the result: the pipeline stages, training and validation curves, the
   label distribution, per-head metrics, a confusion matrix, and real screenshots of the
   outputs.
3. **Offline and reproducible.** Self-contained HTML (inline images/CSS, no CDN, no network
   at view time); every image produced by a script from a real run.
4. **One-command start.** The whole demo must launch from a single command with **no
   arguments**, and ideally from one double-clickable file at the repo root — nothing may
   have to be typed in front of an audience.

## Backlog — do ONE item per iteration, in this order

1. **Training diagnostics.** Extend `scripts/train_model.py` to record per-epoch training and
   validation loss for the real run, and to emit figures into `experiments/figures/`: loss
   curves, quality-label distribution, per-theme F1, per-intent F1, and a quality confusion
   matrix. Add a `--figures-dir` flag; keep the existing CSV output unchanged; add tests for
   the new metric helpers.
2. **`demo/process.html`** built by `scripts/make_process_gallery.py`: an image gallery of the
   working and training process. Each tile is a generated figure with a one-line caption and
   the script that produced it. Include a walkthrough strip generated from a real move:
   board with theme squares coloured -> the MoveReport fields -> the verified explanation ->
   the model's head outputs. Link the page from `demo/index.html`.
3. **`scripts/demo_run.py`** — the live path, **zero-argument by default**: with no options it
   analyses a built-in showcase position, prints the verified explanation, writes the JSON
   report, and renders a board PNG. `--pgn FILE` / `--fen ... --move ...` override the default
   for anyone who wants to bring their own position.
4. **One-command launcher + `DEMO.md`.** Add `run_demo.cmd` at the repo root: one
   double-clickable file that builds any missing artefacts, runs the showcase, and opens
   `demo/index.html` in the default browser. Refresh `DEMO.md` to lead with "double-click
   `run_demo.cmd`" and regenerate every demo page so disk matches the scripts.

## Definition of done

- `experiments/figures/` holds figures from an **actual** training run, not mock data.
- `demo/process.html` opens offline and shows those figures with captions.
- `scripts/demo_run.py` with **no arguments** produces a text explanation, a JSON report and a
  board PNG for its built-in showcase position.
- `demo/index.html` links to the process gallery; `DEMO.md` documents the live run.
- The demo starts from a single command with no arguments, or by double-clicking
  `run_demo.cmd`; nothing has to be typed live.
- `pytest` passes with Stockfish; `ruff check` / `ruff format --check` are clean.
- Each step appended to `experiments/log.csv`; `PROGRESS.md` updated.

## Each iteration

1. Verify green first: `.venv\Scripts\python.exe -m pytest -q` and
   `ruff check src tests eval scripts`. If either is red, fix that before anything else.
2. Do exactly ONE backlog item. Add or extend tests. Run `pytest` and `ruff` before marking it
   done — never mark a step done while tests fail.
3. Append one row to `experiments/log.csv`; note the change in `PROGRESS.md`.
4. If backlog items remain, schedule the next check with `schedule_wakeup`. Once all four are
   done and green, stop the loop (`schedule_wakeup` with `stop: true`) — do not invent work.

## Constraints

- Add alongside existing code; never modify passing code to make room for a new item.
- Offline only: no downloads, no CDN, no network at view time. Never write the paper or slides.
- Prefer a figure a human reads in two seconds over a number buried in a paragraph.

## Current state (update as work lands)

- M0–M5 DONE; explanation layer, gallery, landing page and PBL report done (PROGRESS §11–14).
- **Backlog item 1 DONE** — training diagnostics: `experiments/figures/` holds loss curves,
  label distribution, per-theme F1, per-intent F1, a confusion matrix and `per_label_f1.csv`
  from a real run (PROGRESS §15).
- **Backlog item 2 DONE** — `scripts/make_process_gallery.py` -> `demo/process.html` (real-move
  walkthrough + training figures + model head outputs), linked from `demo/index.html`
  (PROGRESS §16).
- **Backlog item 3 DONE** — `scripts/demo_run.py`, zero-argument live path (prints the verified
  explanation, writes `demo/live/showcase.json` + `.png`; engine auto-located) (PROGRESS §17).
- **Backlog item 4 DONE** — `run_demo.cmd` (double-click the whole demo) + `DEMO.md` refreshed;
  all demo pages regenerated (PROGRESS §18).

**All four backlog items are complete and green — nothing in this loop remains. Do NOT invent
further work: verify green and stop the loop.**

## Environment

- Windows. Use the in-repo venv: `.venv\Scripts\python.exe`.
- Stockfish 19 at `tools/stockfish/stockfish/stockfish-windows-x86-64-universal.exe`;
  `STOCKFISH_PATH` is set at user scope.
- CLI: `.venv\Scripts\moveexp.exe`; tests: `.venv\Scripts\python.exe -m pytest`.
- `matplotlib` and `python-docx` are installed in the venv for figure/document generation.
- Training data already exists: `data/processed/selfplay.parquet` (40 games, 1971 moves).
  Regenerate with `scripts/generate_games.py` then `moveexp batch` if missing.
