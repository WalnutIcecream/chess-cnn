# moveexp — overnight prototype build

Goal: a **demoable prototype with real visual presence** — not the paper, not the slides.
The demo has to survive a live room: something a supervisor can *look at* and understand in
seconds, backed by real numbers, not a wall of text.

## Demo presence (REQUIRED — this is the current focus)

A deep-learning model is invisible on its own, so the build must make the work **visible**
and **checkable** in three ways:

1. **Visual** — boards with the played move highlighted *and* the detected theme squares
   coloured; a landing page that ties the whole story together.
2. **Results** — real metrics rendered as charts, not prose: model vs majority baseline for
   every head (quality / theme / intent), read straight from
   `experiments/model_vs_rules.csv`.
3. **Conceptual** — a one-glance diagram of the pipeline
   (engine -> symbolic rules -> weak labels -> neural model -> verified explanation) plus
   one-line definitions of quality / theme / intent, so the model is not a black box.

Target artefacts (each one command, self-contained, opens offline):

- `scripts/make_gallery.py` -> `demo/gallery.html` — move-by-move, theme squares coloured.
- `scripts/make_site.py`    -> `demo/index.html`   — concept diagram + results charts +
  curated highlights, linking to the gallery.
- `DEMO.md` — the exact demo runbook, pointing at `demo/index.html`.

## Definition of done

1. `demo/index.html` opens offline and shows the pipeline concept diagram, the results
   charts (model vs baseline), and a curated set of striking moves with coloured boards.
2. `demo/gallery.html` renders a real game move-by-move with the played move AND the
   detected theme squares highlighted.
3. `DEMO.md` is the exact 2-minute demo script and points at `demo/index.html`.
4. `pytest` passes with Stockfish; `ruff check` / `ruff format --check` clean.
5. Every generated artefact is reproducible from a script; steps logged to
   `experiments/log.csv`.

## Current state

- **M0–M4 DONE**: Windows env + Stockfish; explanation layer + `explain` CLI; demo corpus;
  `demo/gallery.html`; `DEMO.md`; `experiments/log.csv`.
- **M5 DONE**: `src/moveexp/model/` (encoder, dataset + game-level split, CNN with quality,
  theme and intent heads), `scripts/generate_games.py`, `scripts/train_model.py`,
  `experiments/model_vs_rules.csv` — see PROGRESS §12.
- **Demo presence DONE**: theme-square highlighting in the gallery; `scripts/make_site.py` +
  `demo/index.html` (concept diagram, results charts, highlights); `DEMO.md` refreshed.
  Verified by a headless-Chrome render. 316 tests pass, `ruff` clean — see PROGRESS §13.

**The definition of done above is met — STOP the loop; no further iteration is required.**
Optional future work, only if an explicit task is given: export the demo pages to PNG/PDF
for slides; broaden the self-play corpus for stronger model numbers; add the `_game_id`
guard noted in PROGRESS §12.

## Each iteration: one bounded chunk

1. Read `PROGRESS.md` and `experiments/log.csv`; do the next unfinished demo-presence item.
   If none remains, verify green and stop — do not invent work.
2. Add or extend tests; run `pytest` and `ruff` before marking anything done.
3. Append one row to `experiments/log.csv`; note the change in `PROGRESS.md` briefly.
4. Stop the loop (`schedule_wakeup` with `stop: true`) once `demo/index.html` and the
   highlighted gallery exist and are green — or once a step clearly cannot be done cleanly;
   in that case revert the partial change first and leave the repo green.

## Constraints

- Add alongside existing code; never modify passing code to make room for something new.
- Self-contained HTML only: inline CSS/SVG, no CDN, no network at view time.
- Prioritise *demoability* over research completeness: a chart a human can read beats a
  metric nobody sees.

## Environment

- Windows. Use the in-repo venv: `.venv\Scripts\python.exe`.
- Stockfish 19 at `tools/stockfish/stockfish/stockfish-windows-x86-64-universal.exe`;
  `STOCKFISH_PATH` is set at user scope.
- CLI: `.venv\Scripts\moveexp.exe`; tests: `.venv\Scripts\python.exe -m pytest`.

## Never

- Download large Lichess corpora or run multi-hour labelling.
- Start Leela probing.
- Write the paper or slides.
