# Chess Move Explainer — Progress & Status Report

> Auto-generated status snapshot. Last updated: 2026-10-18.

## 1. Project overview

**Goal:** a system that explains the *intent, tactical importance, and positional effect* of
a chess move. Three layers, built in order:

1. **Symbolic layer** (Stages 1–2): Stockfish measures how good/critical a move is; hand-written
   `python-chess` rules detect tactical + positional themes and derive intent tags. Output is a
   structured `MoveReport` per move.
2. **Dataset layer** (Stage 3): run the symbolic layer at scale over sampled positions to produce
   a weakly-supervised labelled dataset. **Superseded for tactics**: the Lichess puzzle database
   provides independent, human-curated labels, so concepts are now trained and measured against
   real ground truth instead of our own rules (see §19 and `docs/DATASETS.md`).
3. **Learning layer** (Stages 4–5): a neural net predicts the labels from the board alone, then an
   LLM turns verified reports into prose.

**Repo:** `/home/walnut/chess-ai` (Python 3.11+, package `moveexp`).

**Environment used for this work (NixOS, 2026-10-18):**
- `nix-shell` (the project's `shell.nix`) for `libstdc++`/`zlib`/`zstd`, then an in-repo
  `.venv` (`pip install -e '.[dev]'`, CPU `torch`)
- Stockfish: **not required** for the puzzle layer (all detectors are pure `python-chess`)
- Lint/format: `ruff`

---

## 2. Status at a glance

| Metric | Value |
| --- | --- |
| Milestones complete | symbolic layer, explanation layer, demo, **data layer**, **puzzle benchmark**, **concept classifier**, **detector precision pass** (see `README.md` roadmap) |
| Test suite | **384 passed, 18 skipped** (402 collected); engine tests auto-skip without Stockfish |
| Lint / format | `ruff check` clean, `ruff format --check` clean |
| Theme detectors registered | **54** (40 original + 14 puzzle-tag tactics) |
| Static intent detectors | **9** (+ 2 engine-backed threat tags, opt-in) |
| Frozen vocabularies | 54 themes · 11 intents · 8 quality labels (`DATASET_VERSION` = `v2`) |
| Concept classifier (300k rows) | micro F1 0.412 / macro F1 0.374 under per-tag thresholds (top-5 baseline 0.221 / 0.046) |
| Line coverage of the brief | Sections 5–6 (Stages 1–2) implemented; Stage 3 realised via the puzzle corpus |

---

## 3. Milestone status

| # | Milestone (brief §14) | Status |
| --- | --- | --- |
| M1 | Skeleton + engine core | ✅ done (opencode) |
| M2 | Theme framework + tactics + material + SEE + puzzle benchmark | ✅ done (opencode started, continuation finished) |
| M3 | Positional layer (king-safety / structure / activity / features) | ✅ done (folded into M2 by the session) |
| M4 | Intent + full pipeline + `analyze-pgn`/`batch` CLI + Parquet + README | ✅ done (folded into M2) |
| M5 | Data acquisition (downloader + streaming `.zst` readers) | ⏳ pending |
| M6 | Sampling + game-level splits | ⏳ pending |
| M7 | Bulk labelling, label audit, dataset stats | ⏳ pending |
| M8 | Neural model | ⏳ pending |
| M9 | Explanation layer (prompt + verifier) | ⏳ pending |
| M10 | (optional) Leela concept probing | ⏳ pending |

> The opencode session collapsed the brief's M2/M3/M4 into a single "M2" todo block that
> covers the entire symbolic layer. This report follows that working plan.

---

## 4. Work done by the opencode session (recovered from session DB)

The session `ses_f0680409dffeSUGgzDfcwPbaP2` built **Milestone 1** and the **front half of
Milestone 2** before stopping.

**Milestone 1 — skeleton + engine core (complete):**
- `pyproject.toml` (deps + optional `torch`/`dev` extras, `moveexp` console script, pytest/ruff config)
- `config.py` (paths, engine defaults, thresholds, `THEME_VOCAB`/`INTENT_VOCAB`, piece values)
- `schema.py` (`LineInfo`, `QualityInfo`, `MoveReport`, `GameReport`, Parquet flattening, multi-hot vectors)
- `engine/client.py` (`StockfishClient`, `AnalysisLimit`, crash/restart, MultiPV, `analyse_pair`)
- `engine/cache.py` (WAL SQLite cache keyed by normalized FEN + limit + MultiPV)
- `engine/eval_utils.py` (the single perspective-conversion module; win-prob logistic, mate folding)
- `analysis/move_quality.py` (loss→label bands, `great`/`brilliant` in `classify_special`)
- `analysis/criticality.py` (only-move, sharpness, forcing, is_critical)
- `cli.py` (`analyze-move`, `vocab`), `README.md`, `data/` placeholders
- Test suite: `test_eval_utils`, `test_engine_client`, `test_move_quality`, `test_criticality`, `test_cli`, `conftest.py`
- Notable bugs it caught & fixed: illegal FEN crash (SF18), `MultiPV` via `multipv=` not `options=`,
  `analyse()` has no `timeout`, forced-mate win-prob 1.0/0.0, value-ordered `gap_to_second_wp`.

**Milestone 2 — partial:**
- `analysis/see.py` (SEE: memoized minimax, en passant, actual-attacker, `is_sacrifice`) + `test_see.py`
- `analysis/features.py` (`FeatureSnapshot`, `snapshot`, `positional_delta`) + `test_features.py`
- `analysis/themes/base.py` (`ThemeHit`, `DetectionContext`, `REGISTRY`, `@detector`, `run_all`) + `test_themes_base.py`
- `analysis/themes/common.py` (shared attack/defence counting, piece values)
- `analysis/themes/tactics.py` (15 tactical detectors)
- `analysis/themes/material.py` (drafted — **left buggy**, was the in-progress todo)
- `tests/positions.py` (legal board builders)

---

## 5. Work completed in this continuation

**Material detectors (finished + fixed):**
- Fixed `detect_simplification` (inverted condition meant it never fired) — now = even exchange of
  minor-or-better pieces.
- Cleaned `detect_promotion_threat` (dead code) and removed the duplicated local `piece_value_cp`.
- Corrected `detect_sacrifice`/`detect_trade` docstrings to match the static (SEE-only) behaviour.
- Added `tests/test_theme_material.py`.

**Tactical detectors (tests + bug fix):**
- Added `tests/test_theme_tactics.py` — positive + negative cases for all 15 detectors.
- Fixed `detect_overloaded_defender` (was counting our attackers on one piece; now correctly finds
  one enemy piece that is the *sole* defender of two attacked targets).

**Positional detectors (new):**
- `analysis/themes/king_safety.py` (`exposes_king`, `shelters_king`, `weakens_opponent_king`) + tests.
- `analysis/themes/structure.py` (passed/isolated/doubled/backward, islands, breaks, `creates_*`) + tests.
- `analysis/themes/activity.py` (outpost, rook files/seventh, bishop pair, bad bishop, development,
  centre control) + tests.
- Exposed public pawn helpers in `features.py` (`is_passed_pawn`, `is_isolated_pawn`, `is_backward_pawn`,
  `is_doubled_pawn`, `pawn_file_groups`, `pawn_island_count`) and refactored `_pawn_structure` onto them.
- Fixed `_is_stuck` so a *blocked* pawn (e4 vs e5) is no longer mislabelled *backward*.

**Intent layer (new):**
- `analysis/themes/intent.py` — `IntentTag` model + registry, `IntentContext`, 9 static detectors,
  and an optional null-move `threat_probe` (`creates_threat` / `parries_threat`).
- Added `confidence` to `IntentTagModel` in `schema.py`.
- Added `tests/test_intent.py`.

**Pipeline + CLI (new):**
- `pipeline.py` — `analyse_move` (full `MoveReport`: quality + criticality + themes + positional delta
  + intent, with engine-confirmed `brilliant`) and `analyse_game` (one engine reused per game).
- `cli.py` — rewired `analyze-move` through the pipeline; added `analyze-pgn` and `batch` (parallel
  `--workers`, Parquet output).

**Puzzle benchmark (new):**
- `eval/puzzle_benchmark.py` — maps Lichess tags → detectors, runs them on solution moves, reports
  precision/recall/F1 per theme to CSV (reservoir-sampled, fixed seed).
- Added `tests/test_puzzle_benchmark.py`.

**Docs:** updated `README.md` (M2 status, layout, report example, roadmap, null-move cost note).

---

## 6. Code structure (current)

```
src/moveexp/
  config.py            thresholds, paths, frozen vocabularies (40 themes / 11 intents)
  schema.py            LineInfo / QualityInfo / MoveReport / GameReport + Parquet + multi-hot
  engine/
    client.py          StockfishClient: process lifecycle, MultiPV, crash recovery
    cache.py           WAL SQLite analysis cache
    eval_utils.py      the ONLY module that changes evaluation perspective
  analysis/
    move_quality.py    win-probability loss → quality label
    criticality.py     only-move / sharpness / forcing / is_critical
    see.py             static exchange evaluation
    features.py        PositionalDelta + public pawn helpers
    themes/
      base.py          ThemeHit, DetectionContext, detector registry
      common.py        shared attack/defence counting
      tactics.py       15 tactical detectors
      material.py      6 material detectors
      king_safety.py   3 king-safety detectors
      structure.py     8 pawn-structure detectors
      activity.py      8 activity detectors
      intent.py        9 static intent detectors + null-move threat_probe
  pipeline.py          analyse_move / analyse_game
  cli.py               analyze-move / analyze-pgn / batch / vocab
tests/                 279 tests (engine-marked tests auto-skip without Stockfish)
eval/puzzle_benchmark.py   detector precision/recall vs Lichess puzzle tags
data/{raw,cache,processed,audit}/   git-ignored working dirs
```

---

## 7. Detector inventory

**Themes (40 registered):**
- *tactics (15):* fork, pin, skewer, x_ray, discovered_attack, discovered_check, double_check,
  hanging_piece, threat_created, hanging_piece_defended, back_rank_mate, trapped_piece,
  overloaded_defender, deflection, interference. (`decoy` is not a theme — it needs the opponent's
  reply, which is a fact about a later position, so it is absent from the vocabulary entirely.)
- *material (6):* capture, sacrifice, trade, simplification, promotion, promotion_threat.
- *king safety (3):* exposes_king, shelters_king, weakens_opponent_king.
- *structure (8):* passed_pawn, creates_passed_pawn, isolated_pawn, creates_isolated_pawn,
  doubled_pawn, backward_pawn, pawn_island, pawn_break.
- *activity (8):* outpost, rook_open_file, rook_semi_open_file, rook_seventh, bishop_pair,
  bad_bishop, develops_piece, controls_center.

**Intents (9 static + 2 engine):**
- static: develops, castles, simplifies, attacks_king, improves_piece, restricts_opponent,
  defends_material, prepares_break, trades_defender.
- engine (opt-in `--null-move-probes`): creates_threat, parries_threat.

---

## 8. Test status

- `STOCKFISH_PATH=/tmp/opencode/stockfish/src/stockfish pytest` → **279 passed**.
- `pytest` (no engine) → engine-marked tests skip; pure-geometry tests still pass.
- `ruff check src tests eval` → clean. `ruff format --check src tests eval` → clean.

Coverage highlights (per the brief §13): every detector has positive **and** negative cases on
hand-built legal FENs (real fork vs fake fork, absolute/relative pin, sacrifice vs blunder, etc.);
eval/mate/perspective conversions are pinned with mirrored positions; SEE has single- and
multi-attacker exchange cases.

---

## 9. Known issues & notes

- **NixOS data-stack caveat:** `numpy`/`pandas`/`pyarrow` are installed in the venv but fail to
  import unless `libstdc++.so.6` is on the loader path. This only affects the `batch` Parquet
  export (and future Stage 3 tooling), not the symbolic layer — the library imports them lazily.
  Workaround:
  ```bash
  export LD_LIBRARY_PATH=/nix/store/3b7njvjfc2w5lhj1jklrsw4lq7nwypri-gcc-15.2.0-lib/lib:$LD_LIBRARY_PATH
  ```
- **Mate-unit ambiguity** (documented in `eval_utils.py`): raw Stockfish mate distances are stored
  un-converted; only their magnitude is used.
- **Heuristic labels are expected to be noisy.** Detectors are static/geometric by design; the
  brief explicitly plans a manual label audit (M7) before scaling up or training.
- **`sacrifice` is static** (SEE material give-up); the *engine confirmation* that it's a good
  sacrifice (not a blunder) lives in `classify_special` / the pipeline, not the theme detector.

---

## 10. Next steps (pending milestones)

1. **M5 — data acquisition:** resumable downloader + streaming `.zst` readers (PGN / puzzle CSV /
   eval-DB lookup), with small fixture-sample tests. Confirm which Lichess file formats are verified.
2. **M6 — sampling & splits:** dedupe, opening-ply skip, oversampling, game-level train/val/test
   (leakage test required).
3. **M7 — bulk labelling:** two-tier resumable parallel labeller, `audit_labels.py`, `dataset_stats.py`.
   **Stop here for manual label review** before training.
4. **M8 — model:** `encode.py`, `dataset.py`, `network.py`, `train.py`, `evaluate.py` (+ CPU debug config).
5. **M9 — explanation:** `explain/` prompt template + verifier, `explain` CLI.
6. **M10 (optional) — Leela probing.**

---

## 11. Prototype build — Windows, 2026-10-05

The symbolic layer was developed on NixOS; this session stood it up on Windows and added
the demo-facing pieces. Environment: Python 3.13 venv, Stockfish 19 (official
`sf_19` `windows-x86-64-universal` build in `tools/`, git-ignored), `STOCKFISH_PATH` set
at user scope. Full suite: **298 passed**, `ruff check` / `ruff format --check` clean.

**Added**

- **Explanation layer** (`src/moveexp/explain/`): `facts.py` derives checkable clauses from
  a `MoveReport`; `render.py` orders them into prose; `verify.py` re-derives every claim
  from the same report and drops anything the report does not support; `api.py` wraps the
  pipeline. No new inference — every sentence is traceable to a report field.
- **`moveexp explain` CLI**: `--fen/--move` for one move, `--game` for a whole game,
  `--json` for the structured report + claims, `--out` to write a file.
- **Demo corpus + scripts**: `demo/games/opera.pgn`, `demo/games/immortal.pgn`;
  `scripts/build_demo.py` (games -> `demo/out/*.md` + `*.json`);
  `scripts/make_gallery.py` (JSON -> self-contained `demo/gallery.html`, inline board SVGs,
  quality badges, grouped claims, per-move evidence tables).
- **`DEMO.md`** runbook and **`experiments/log.csv`**.

**Verified numbers from this build**

| Artefact | Result |
| --- | --- |
| Test suite | 298 passed (12 explain + 3 gallery tests are new) |
| Demo games | Opera Game 33 plies, Immortal Game 45 plies |
| Gallery | 78 cards, 2638 KiB, 78/78 moves fully verified |

**Windows fixes made**

- Console streams reconfigured to UTF-8 in the CLI (em dashes were mangled under cp1252).
- `format_game_explanation` move-numbering bug (used a report attribute on an explanation).
- Positional feature deltas suppressed on a decided (forcing-win) move — they are artifacts
  of the terminal board, not intent signal.

**Still open (unchanged):** M5 data acquisition, M6 splits, M7 bulk labelling, M8 model.
The neural model (Stage 4) remains the main research contribution and is not started.

---

## 12. M5 stretch — tiny neural baseline (2026-10-05)

A first CPU-only neural baseline was added on top of the rule labels, to test whether the
labels are learnable from the board alone. New code: `src/moveexp/model/` (encoder,
dataset + game-level split, tiny CNN with quality, theme and intent heads),
`scripts/generate_games.py` (self-play corpus, **no downloads**) and
`scripts/train_model.py` (train + evaluate + majority baseline).

**Data.** 40 Stockfish self-play games (depth 6, sampling the top 3 moves), 1971 moves,
labelled by the existing pipeline at depth 8 and split by game id (1571/200/200).

**Results** (`experiments/model_vs_rules.csv`, `with_move` variant, weighted losses):

| head | metric | model | majority baseline |
| --- | --- | --- | --- |
| quality | accuracy | 0.200 | 0.445 |
| quality | macro F1 | 0.152 | 0.088 |
| theme | micro F1 | 0.307 | 0.246 |
| theme | macro F1 | 0.220 | 0.022 |
| intent | micro F1 | 0.271 | 0.000 |
| intent | macro F1 | 0.203 | 0.000 |

**Reading.** *Tactical themes are the strongest signal* — the CNN beats a trivial prior
baseline by ~10x on macro F1 and ~25% on micro F1. *Intents* are also learned (0.27 micro
/ 0.20 macro F1), but note the baseline there degenerates to all-off (no intent is common
enough to have majority prevalence), so that bar is weak. *Move quality* stays below the
majority-class baseline on accuracy (0.20 vs 0.445), yet its macro F1 now **beats** the
baseline (0.152 vs 0.088) — the extra intent head acts as a regulariser. The architecture
is not the limit: a 96-sample overfit run reaches 0.96 quality accuracy, so the quality
result is a data/label-difficulty finding and belongs in the paper's error analysis.
Encoding the played move barely changed the ranking (theme macro F1 0.220 with vs 0.238
without; intent 0.203 vs 0.210).

**Caveats (statement of scope).** The baseline is a majority/prior predictor, **not "the
rules"** — the rules generated the labels, so this measures *learnability*, not
correctness. No independent ground truth (puzzle tags / human labels) is used yet, and the
labels are known to be noisy. Treat these numbers as a first signal, not a verdict.

**Latent bug found (not fixed here).** `pipeline._game_id` returns the `Site` header
whenever it is non-empty, and python-chess defaults `Site` to `"?"`, so PGNs without a
real Site all collapse to a single game id (this initially merged all 40 self-play games
and would have silently destroyed the game-level split). Worked around in
`generate_games.py` by writing a unique Site per game; Lichess games are unaffected
because they carry a real Site. A guard in `_game_id` is a separate, later change.

---

## 13. Demo presence — visual landing page (2026-10-05)

The demo now has a front door: `demo/index.html`, built by `scripts/make_site.py`. It is a
single self-contained page with three sections, so a supervisor can check the work in a
room instead of reading a transcript:

- **Concept** — an inline-SVG pipeline diagram (engine -> symbolic rules -> weak labels ->
  CNN -> verified explanation) and one-line definitions of quality / theme / intent.
- **Results** — the numbers from `experiments/model_vs_rules.csv` drawn as bar charts
  (green = model, grey = majority baseline) per head, with the same values in a table.
- **Highlights** — the most striking moves across the demo games, with the detected theme
  squares shaded blue and the played move shaded yellow, linking to the full gallery.

`demo/gallery.html` was extended to colour the detected **theme squares** on every board,
not just the played move, so the tactics the detectors found are visible rather than
asserted.

Both pages are offline and self-contained (inline CSS/SVG, no CDN, no network at view
time). Verified by rendering headlessly with Chrome: the landing page shows the 5-box
pipeline, 3 charts and 6 highlight boards; the gallery shows 78 cards with blue theme
shading. New tests: `tests/test_site.py`, plus theme-square cases in `tests/test_gallery.py`.

---

## 14. PBL-2 report (2026-10-05)

`scripts/make_pbl_report.py` generates `PBL_Report_Chess_Move_Intent.docx` (repo root, also
copied next to the original in `Downloads/`). It reproduces the exact skeleton of the
submitted PBL-2 report — title page, certificate, abstract, list of tables, list of figures,
table of contents, sections 1–11 with the same subsection numbering, tables 4.1/6.1/7.1/8.1/9.1,
figures 4.1/5.1/6.1/8.1, and the References section — with all content rewritten for the
current system: the design decisions and why they were taken, the problems hit and their
fixes, and the limitations (including why the Lichess puzzle data was deliberately deferred).

Four figures are generated by the script (architecture, module flowchart, sample terminal
output, model-vs-baseline chart). The contents list is a Word `TOC` field carrying the section
list as cached text: open the file in Word and press Ctrl+A then F9 to populate the page
numbers. The Page No. columns in the List of Tables / List of Figures are inherited from the
original layout and should be confirmed after pagination.

---

## 15. Demo build — training diagnostics (2026-10-05)

First item of the presentation/demo loop (see `.commandcode/loop.md`). `scripts/train_model.py`
now records per-epoch training and validation loss and, when given `--figures-dir`, writes the
process figures the upcoming gallery will display:

- `loss_curves.png` — training vs validation loss per epoch.
- `label_distribution.png` — move-quality label counts over all labelled moves.
- `theme_f1.png`, `intent_f1.png` — per-label F1 on the held-out games.
- `quality_confusion.png` — row-normalised quality confusion matrix.
- `per_label_f1.csv` — the same per-label F1 values as data.

New pure helpers (`confusion_matrix`, `per_label_f1`, `quality_label_counts`) with tests in
`tests/test_train_model.py`; the results CSV is unchanged. The real run is instructive: the
training loss falls to about 2.5 while the validation loss rises past 8 after roughly epoch
20, i.e. the model overfits a 1571-row training set — which is precisely why the trainer keeps
the best-validation checkpoint rather than the final weights. 321 tests pass, `ruff` clean.

---

## 16. Demo build — process gallery (2026-10-05)

Second item of the demo loop. `scripts/make_process_gallery.py` builds `demo/process.html`, an
offline gallery in two halves:

- **Working process** — a walkthrough strip taken from a real move in the corpus (Morphy's
  10.Nxb5, ply 18): the board with the detected theme squares coloured, the rule report
  (quality, themes, intent, positional change), the verified explanation, and the trained
  model's own head outputs for the same move, annotated with whether it agrees with the rule
  label.
- **Training process** — the five figures from `scripts/train_model.py --figures-dir`, each
  captioned with the script that produced it.

`train_model.py` gained an optional `--save` flag so the gallery can show real per-move model
predictions; the checkpoint is `experiments/model.pt` (git-ignored, regenerable). Images are
embedded as base64 and the board is inline SVG, so the page opens with no network. It is
linked from the `demo/index.html` navigation and was verified by a headless-Chrome render.
6 new tests; 327 pass, `ruff` clean.

---

## 17. Demo build — live runner (2026-10-05)

Third item of the demo loop. `scripts/demo_run.py` is the live path and is **zero-argument by
default**: with no options it explains Morphy's 10.Nxb5 (read from `demo/out/opera.json`, with a
built-in mate-in-one fallback), prints the verified explanation to the terminal, writes
`demo/live/showcase.json` (report + explanation + claims) and renders `demo/live/showcase.png` —
a board with the detected theme squares in blue, the played move in yellow, and a move arrow.
`--fen/--move` and `--pgn` override the default.

The engine is located automatically (STOCKFISH_PATH, then the repo's `tools/` drop, then PATH),
so the command needs no environment setup on the demo machine, and the console streams are
reconfigured to UTF-8 so the em dashes print correctly on Windows. 7 new tests; 334 pass,
`ruff` clean. Verified by running the zero-argument form and inspecting the rendered board.

---

## 18. Demo build — one-command launcher (2026-10-05)

Final item of the demo loop. `run_demo.cmd` in the repository root is the whole demo: one
double-clickable, argument-free batch file that runs the live showcase
(`scripts/demo_run.py`) and then opens `demo/index.html` in the default browser. It resolves its
own directory (`%~dp0`) so it works when double-clicked from anywhere, prefers the in-repo venv
Python and falls back to `python`, honours `MOVEXP_NO_BROWSER=1` to skip the browser (used for
the smoke test), and pauses so a failure is readable.

`DEMO.md` now leads with the double-click and the one-line fallback, then the pages, then the
2-minute script. All three demo pages were regenerated from their scripts so disk matches the
code, and the whole chain was smoke-tested end to end with the browser suppressed.

This completes the demo/presentation backlog (items 1–4): training diagnostics, the process
gallery, the zero-argument live runner, and the one-command launcher. 334 tests pass, `ruff`
clean.

---

## 19. Real dataset, tagged concepts, and a measured detector benchmark (2026-10-18)

The core problem until now: the only trained artifact ran on 40 self-play games whose labels
came from *our own rules*, so it measured imitation, not correctness. This section replaces
that with an independent source and the first honest numbers about detector quality.

### What was built

- **Data layer** (`src/moveexp/data/`): a resumable, stdlib-only downloader and streaming
  `.zst` readers, plus `scripts/download_data.py`. The Lichess puzzle database
  (`lichess_db_puzzle.csv.zst`, 6.16M tagged puzzles, CC0) is now on disk.
- **Tag taxonomy + mapping** (`src/moveexp/data/puzzle_themes.py`): the Lichess tag vocabulary
  and its injective mapping onto `THEME_VOCAB`, shared by the benchmark and the dataset builder
  so both measure the same label space. Phase/length/strength tags are dropped.
- **14 new tactic detectors** (`themes/tactics_ext.py`), including **line-aware** ones: the
  `DetectionContext` now carries an optional continuation, so `attraction`, `clearance` and
  `intermezzo` — facts about the *line*, not one position — are detectable for the first time
  (this is the same reason `decoy` was absent before). `THEME_VOCAB` is now 54 and
  `DATASET_VERSION` is `v2`.
- **Puzzle benchmark** (`eval/puzzle_benchmark.py`): reads the `.zst` directly, maps tags,
  passes the solution continuation, and reports per-theme precision/recall/F1.
- **Concept dataset + classifier**: `scripts/build_puzzle_dataset.py` (one row per puzzle key
  move, targets = mapped Lichess tags) and `scripts/train_concepts.py` (the `MoveNet` theme
  head, per-tag thresholds tuned on validation).
- Also fixed while here: `shell.nix` now puts `zlib`/`zstd` on the loader path (numpy and
  pyarrow would not import without it); `matplotlib`/`python-docx` were missing from
  `pyproject.toml`; and `pipeline._game_id` no longer treats python-chess's default
  `Site == "?"` as a real game id (the latent split-leakage bug from §12).

### Result 1 — the concept classifier learns real concepts

`scripts/build_puzzle_dataset.py --n 200000` -> 120,610 rows over 27 tactic themes;
`scripts/train_concepts.py` on 96,488/12,061/12,061 (train/val/test, split by puzzle).

| prediction | micro F1 | macro F1 |
| --- | --- | --- |
| model | **0.436** | **0.313** |
| prevalence baseline | 0.000 | 0.000 |

The baseline is degenerate (no tag occurs in >50% of rows, so the per-tag majority predictor
is all-off), so read these as "the network recovers real, independent concepts the trivial
prior cannot", not as a strong bar. Best per-tag F1: `attacking_f2f7` 0.81,
`back_rank_mate` 0.74, `kingside_attack` 0.70, `advanced_pawn` 0.62, `fork` 0.50. Eight rare
tags score 0.00: the global threshold (0.65, tuned for macro F1) never fires on them, which is
what per-tag thresholds are for (next step).

### Result 2 — the detector benchmark, and what it actually measures

20,000 sampled puzzles, 17,067 tagged tactics (`data/audit/puzzle_benchmark.csv`):

| theme | gold | detected | P | R | F1 |
| --- | --- | --- | --- | --- | --- |
| smothered_mate | 75 | 75 | 1.00 | 1.00 | 1.00 |
| en_passant | 32 | 32 | 1.00 | 1.00 | 1.00 |
| promotion | 501 | 504 | 0.99 | 1.00 | 1.00 |
| double_check | 104 | 103 | 1.00 | 0.99 | 1.00 |
| under_promotion | 8 | 10 | 0.80 | 1.00 | 0.89 |
| advanced_pawn | 1,219 | 1,557 | 0.67 | 0.85 | 0.75 |
| fork | 2,586 | 7,721 | 0.33 | 0.99 | 0.50 |
| discovered_attack | 1,058 | 2,380 | 0.31 | 0.69 | 0.43 |
| pin | 1,246 | 6,306 | 0.20 | 1.00 | 0.33 |
| ... | | | | | |
| x_ray | 71 | 6,561 | 0.00 | 0.23 | 0.00 |
| interference | 59 | 1,181 | 0.00 | 0.02 | 0.00 |
| overloaded_defender | 0 | 1,150 | 0.00 | 0.00 | 0.00 |

**The important finding is that the low rows are mostly not a tuning problem.** Lichess tags
are of two kinds, and the benchmark conflates them:

1. **move-level motifs** — `fork`, `pin`, `skewer`, `smothered_mate`, `en_passant`,
   `double_check`, `promotion`. "This move forks" is decidable from the position, and those
   detectors do well (F1 0.5–1.0).
2. **puzzle-level descriptions** — `kingside_attack`, `quiet_move`, `defensive_move`,
   `attraction`, `clearance`, `intermezzo`, `capturing_defender`, `x_ray`, `hanging_piece`.
   These describe *the puzzle as a whole* ("this is a kingside attack"), so a per-move rule is
   structurally mismatched to the label however it is tuned.

Tightening the three worst new detectors (an in-between move now needs an exchange in
progress; a wing attack now has to hit an enemy *piece* on the wing; a clearing move must be
quiet) moved precision by ~0.00–0.01 and total detections by 20–45% — evidence for exactly
that reading. `pin` (R = 1.00) and `fork` (R = 0.99) show the other half of the same story: the
motif is found, but the tag requires it to be the *point* of the puzzle.

Next steps, in order: a per-tag threshold for the classifier, splitting the benchmark report
into move-level vs puzzle-level tags so the two are not averaged together, and a real
move-quality corpus from Lichess games (`README.md` roadmap M7).

389 tests collected; 371 pass and 18 engine tests skip without Stockfish. `ruff` clean.

---

## 20. Loop item 1 — tag groups and an offline puzzle fixture (2026-10-20)

Section 19 read the two tag kinds off the numbers by hand. This item makes the split part of
the code, and gives every later item a fast, offline way to measure.

### What landed

- `moveexp.data.puzzle_themes` now partitions the 28 mapped tags into **`MOVE_LEVEL_TAGS`**
  (19 — decidable from the position and its move) and **`PUZZLE_LEVEL_TAGS`** (9 — true of the
  whole puzzle), with `tag_group()` / `theme_group()` and derived theme sets. Tests pin the
  partition as total and disjoint over the mapping domain.
- `eval/puzzle_benchmark.py` reports in those groups: a `group` column in the CSV, one table
  per group, and a `group_scores()` summary giving micro and macro F1 per group (they measure
  different things — "how good are these detectors overall" vs "how good is the average
  detector" — so both are printed).
- **`tests/data/puzzles_sample.csv`** — a 540-puzzle, 107 KiB fixture covering 27 of the 28
  themes, produced by `scripts/make_puzzle_fixture.py`. It is **stratified**, not random: a
  plain sample would leave `en_passant`/`x_ray`/`interference` with a handful of positives and
  make their F1 noise, whereas up to 20 puzzles per theme keeps every theme measurable. The
  sampler is tested (caps, determinism, dedupe, rare-theme coverage) and `format_puzzle_row()`
  round-trips through the parser so the fixture is written and read by the same code as the
  real corpus.
- `overloaded_defender` has **no** puzzle in the whole corpus — 0 gold in 20,000 — so it is
  unmeasurable and is now known to be, rather than silently reported as F1 0.00.

### The split, measured

| group | themes | micro F1 | macro F1 |
| --- | --- | --- | --- |
| move-level | 19 | **0.242** | **0.407** |
| puzzle-level | 9 | 0.142 | 0.146 |

(20,000-puzzle corpus, `data/audit/puzzle_benchmark.csv`.) On the 540-puzzle fixture the same
ordering holds — move 0.350 micro / 0.436 macro vs puzzle 0.248 / 0.265 — and
`tests/test_puzzle_benchmark.py` asserts it, so the claim is now checked in CI rather than
argued in prose. The separation is clearest on macro F1 (2.8×), which is the honest reading:
per-theme, the move-level detectors include near-perfect ones (`promotion`, `en_passant`,
`smothered_mate`, `double_check`, `under_promotion` all ≈ 1.00) while the best puzzle-level
theme reaches 0.51.

14 new tests; 385 collected, 367 pass and 18 engine tests skip without Stockfish. `ruff` clean.

**Next in the loop**: item 2 — a non-degenerate top-k baseline and per-tag decision
thresholds, so the classifier's 8 zero-F1 tags and its meaningless 0.000 baseline are fixed.

---

## 21. Loop item 2 — a real baseline and per-tag thresholds (2026-10-20)

Section 19's classifier reported macro F1 0.313 with **eight tags at exactly 0.00**, and its
only baseline scored 0.000. Both problems had the same root: a single global decision
threshold, and a majority predictor that cannot answer anything on this data.

### What landed (`scripts/train_concepts.py`)

- **`top_k_baseline` / `tune_top_k`** — predict the ``k`` most common training tags on every
  row, with ``k`` chosen by validation **micro** F1. Micro is the right criterion: macro would
  keep rewarding a larger ``k`` (a tag predicted everywhere gets F1 = 2p/(1+p), which rises
  with its prevalence), so macro would just pick the largest ``k``. The majority predictor is
  kept only as the all-off reference, since no tag appears in more than half the rows.
- **`tune_per_tag_thresholds` / `apply_per_tag_thresholds`** — one threshold per tag, each
  maximising that tag's own F1 on validation (a grid of 0.05…0.95, step 0.05). A tag with no
  positive in the tuning set keeps the neutral 0.5 rather than being driven to the bottom of
  the grid against an empty column.
- **Early stopping now tracks the reported metric** — macro F1 under per-tag thresholds — which
  is what raised the validation curve from 0.315 to 0.356 by epoch 8.
- `binary_f1` was added to `moveexp.model.metrics` (a scalar form of the existing private
  helper) so the per-tag tuner and the multi-label metrics share one definition.
- The CSV schema changed (this file is one session old): `model_global`, `model_per_tag`,
  `all_off`, `topk_baseline`, `topk_k`.

### Measured (120,610 rows, 96,488/12,061/12,061 by puzzle)

| prediction | micro F1 | macro F1 |
| --- | --- | --- |
| model, global threshold | 0.436 | 0.313 |
| **model, per-tag thresholds** | 0.384 | **0.349** |
| all-off (= the old "prevalence" baseline) | 0.000 | 0.000 |
| top-3 baseline (k chosen on val) | 0.220 | 0.031 |

Three things to read carefully:

1. **The eight zero tags are gone.** Every tag with test positives now scores something:
   `capturing_defender` 0.188, `en_passant` 0.099, `x_ray` 0.099, `intermezzo` 0.092,
   `double_check` 0.092, `clearance` 0.061, `under_promotion` 0.044, `interference` 0.029. They
   are weak, but they are measured rather than silently zero.
2. **Per-tag thresholds trade micro for macro** (0.436 → 0.384 micro, 0.313 → 0.349 macro).
   That is the expected shape: lowering a rare tag's threshold buys its recall at the cost of
   precision pooled over the common tags. Both numbers are reported so the trade is visible
   rather than hidden behind one headline.
3. **The bar is real now.** The top-3 baseline scores 0.220 micro / 0.031 macro where the old
   "prevalence" baseline scored 0.000, so "the model beats the baseline" is a claim with
   content: 0.384 vs 0.220 micro and 0.349 vs 0.031 macro.

Still true from §19: eight themes have no positive in the test split at all (they are rare in
the corpus), and `overloaded_defender` has no puzzle anywhere, so none of these can be measured
yet.

5 new tests; 389 collected, 371 pass and 18 engine tests skip without Stockfish. `ruff` clean.

**Next in the loop**: item 3 — symmetry augmentation, an LR schedule and early stopping, so the
classifier itself improves rather than only how it is read.

---

## 22. Loop item 3 — a training ablation, and a negative result (2026-10-20)

This item set out to make the classifier better by training it better: symmetry augmentation,
a learning-rate schedule, and early stopping. Two of the three did not help, and the loop's
rule — prefer a measurement over a claim — says the measurement wins.

### What landed (`scripts/train_concepts.py`)

- **`transform_batch` / `augment_batch`** — mirror and colour-flip applied per sample. Both are
  genuine board symmetries (the mover's win probability and every theme label are unchanged).
  The torch implementation has a test pinning it to the numpy reference
  `moveexp.model.encode.augment_planes`, so the two cannot drift.
- **`cosine_lr`** — an explicit cosine decay (base rate → 5% of it), written out rather than
  delegated to a `torch` scheduler so its shape is testable: starts at the base rate, ends at
  the floor, never rises.
- **Early stopping** with `--patience` (default 3), and `--epochs` raised 8 → 10.
- Flags for every ablation: `--augment/--no-augment`, `--schedule none|cosine`, `--patience`.
  The results CSV carries `augment` and `schedule` columns so the ablation lands in one file
  (`experiments/concepts_ablation.csv`).

### The ablation (120,610 rows, 10 epochs each, per-tag thresholds)

| config | micro F1 | macro F1 | val macro F1 (last epoch) |
| --- | --- | --- | --- |
| **plain (10 epochs)** | **0.411** | **0.370** | 0.369 |
| + symmetry augmentation | 0.398 | 0.343 | 0.350 |
| + augmentation + cosine schedule | 0.313 | 0.289 | 0.291 |

Top-3 baseline, unchanged: 0.220 micro / 0.031 macro.

Reading, in the order the evidence supports:

1. **Training longer did help.** The same configuration at 8 epochs (item 2) scored 0.349 macro;
   at 10 epochs it scores 0.370. That is the one improvement this item actually bought.
2. **Augmentation did not help** (0.370 → 0.343 macro). The honest phrasing is "did not help",
   not "hurt": these are single runs on one split, and a 0.027 macro gap is close to run-to-run
   noise. Both augmented runs were *still improving* at the epoch limit (val 0.350 and rising),
   so this compares equal epochs, not equal convergence — augmentation costs convergence speed
   and 10 epochs may simply not be enough budget for it to pay off.
3. **The cosine schedule was the wrong choice for this budget.** Under a 10-epoch cosine the
   last third of training runs at 5e-05, before the model has converged, and it is worse at
   *every* epoch than the constant rate (0.291 vs 0.369 at epoch 10). That is an argument about
   the schedule's time constant, not about schedules in general.
4. Early stopping never fired — every run was still improving at epoch 10 — so it is inert here,
   but it is what will make a longer run safe.

**Both are therefore off by default**, kept as flags with the numbers recorded next to them, and
the default configuration is the measured-best one. Re-running the headline
(`experiments/concepts_vs_tags.csv`) with those defaults reproduces the 0.411 / 0.370 row.

4 new tests (including an end-to-end trainer smoke test on a tiny synthetic dataset);
393 collected, 375 pass and 18 engine tests skip without Stockfish. `ruff` clean.

**Next in the loop**: item 4 — a bigger/cleaner puzzle dataset (all solver moves, FEN dedupe,
richer summary), which is the other lever on the same numbers.

---

## 23. Loop item 4 — puzzle dataset upgrade, and a flat result (2026-10-20)

This item made the dataset builder honest about what it emits and then enlarged the corpus by
2.5×. The enlargement did not move the metric — again a negative result, recorded as measured.

### What landed (`scripts/build_puzzle_dataset.py`)

- **`dedupe_by_position`** — rows are deduplicated by **normalised FEN** (the project's position
  identity: board, side, castling, en passant; counters dropped), keeping the first row of each.
  A repeated position both inflates the set and can leak across the train/test split. On by
  default (`--dedupe/--no-dedupe`).
- **`rating_band` / `RATING_BANDS`** and **`tag_groups`** — every row now records which rating
  bucket it falls in and which tag group(s) its themes belong to (`move`, `puzzle`, or both),
  so the sample's composition is inspectable rather than assumed.
- **A real build summary** — row count, duplicate positions dropped, theme coverage split by
  group, rows by tag group, rows by rating band, and the most common tags.
- `--all-solver-moves` (already present) is what the enlargement used.

### The rebuild (`--n 200000 --all-solver-moves`)

```
wrote 299986 rows to data/processed/puzzles.parquet
  sampled 200000 puzzles; 708 rows dropped as duplicate positions
  themes covered: 27 of 54 (move-level 18, puzzle-level 9)
  rows by tag group:      move 168794 (56.3%) | puzzle 69519 (23.2%) | move puzzle 61673 (20.6%)
  rows by rating band:    <1200 27.4% | 1200-1599 23.3% | 1600-1999 22.2% | 2000-2399 17.3% | 2400+ 9.7%
```

2.5× the previous 120,610 rows. Two things worth noting: only **708** positions were duplicates
(the corpus is close to position-unique, so dedupe is cheap insurance rather than a big
cleanup), and the rating distribution is heavily weighted to the low end, as Lichess puzzles
are.

### The result

| dataset | rows | micro F1 | macro F1 |
| --- | --- | --- | --- |
| key move only (item 3) | 120,610 | 0.4105 | 0.3700 |
| **all solver moves (this item)** | **299,986** | **0.4124** | **0.3740** |

Top-5 baseline: 0.221 micro / 0.046 macro — the model still clears it comfortably.

**2.5× more data bought +0.004 macro F1, which is inside run-to-run noise.** Two changes are
confounded here: the set grew *and* the labels got noisier (`--all-solver-moves` attaches a
puzzle's tags to every solver move, and a long puzzle's tags need not describe each of its
moves). The clean experiment — `--n 400000` key-move-only, same labels, larger — is the obvious
follow-up, and is now cheap to run because the builder reports exactly what it produced.

The honest summary of items 3 and 4 together: for this model and this label space, neither
"train it harder" nor "give it more data" is the binding constraint. That points at the label
space and the model's input, not the training loop — which is why item 5 goes back to the
detectors, the other half of the comparison.

6 new tests; 399 collected, 381 pass and 18 engine tests skip without Stockfish. `ruff` clean.

**Next in the loop**: item 5 — the detector precision pass, with F1 floors pinned on the
offline fixture.

---

## 24. Loop item 5 — detector rewrites, and a criterion that was not met (2026-10-20)

Item 5 asked to rewrite the detectors whose *definition* is wrong (as opposed to merely
mismatched to a puzzle-level tag) and to pin them with an offline guard. The rewrites landed,
the guard landed, and the item's own F1 expectation **did not hold**. Recording that is the
point of the exercise.

### What landed (`src/moveexp/analysis/themes/tactics.py`)

- **`x_ray`** now requires the ray to be **created by this move** — either the moved piece is the
  slider, or the move vacated a square on the line (`_opens_ray`). Before, it reported every
  pre-existing x-ray anywhere on the board on every move, which is not just imprecise: it made
  the explanation layer claim an x-ray the move had nothing to do with.
- **`interference`** now requires the shielded piece to have been **genuinely threatened** before
  the move (or to be the king, i.e. the move blocks a check). Before, any move that happened to
  cross an enemy slider's path counted.
- **`hanging_piece`** now means **undefended**, not merely out-numbered (attackers > defenders).
  A defended piece under two attackers is pressure, not a hanging piece.

### Measured (20,000-puzzle corpus, before → after)

| theme | detections | F1 |
| --- | --- | --- |
| `x_ray` | 6,561 → **4,917** (−25%) | 0.005 → 0.004 |
| `interference` | 1,181 → **654** (−45%) | 0.002 → 0.000 |
| `hanging_piece` | 8,152 → **7,266** (−11%) | 0.047 → 0.040 |
| move-level group, micro F1 | — | 0.242 → **0.253** |
| move-level group, macro F1 | — | 0.407 → 0.407 |

**The item's "F1 improves" criterion is not met.** False-positive volume fell by 11–45% and the
group's micro F1 rose (0.242 → 0.253), but the per-theme F1 for these three is flat to slightly
*worse*: each rewrite also drops a few true positives, and precision stays near zero because the
denominator is still thousands of legitimate-on-the-board motifs against tens of gold.

The reason is the one from §19–20, now confirmed for these three as well: a tag is only applied
when the motif is the **point of the puzzle**, and x-rays, interferences and loose pieces are
everywhere in tactical positions. That is not something a definition can fix, and chasing it
would mean tuning thresholds against a label that is not measuring the thing. So the rewrites
stand on a **correctness** argument rather than a metric one — the reports no longer attribute
other moves' motifs to this move — and the numbers are recorded as they are.

`kingside_attack` / `queenside_attack` were named in the item but are **puzzle-level** by item
1's grouping; their low precision is that mismatch, so they are reported and deliberately not
tuned. A test pins both the measurement and the classification, so changing either is a
deliberate act.

### The regression guard (`tests/test_puzzle_benchmark.py`)

`DETECTOR_EXPECTATIONS` pins, on the committed fixture, a **minimum F1 and a maximum detection
count** for the five near-perfect detectors and the three rewritten ones. Both sides are needed:
an F1 floor alone would be satisfied by the *old* x-ray/interference/hanging definitions, so each
detection ceiling sits below the pre-rewrite count (198 / 51 / 222) and a revert fails offline.
A second test pins the kingside/queenside decision above — they stay measured and stay classified
as puzzle-level — so revisiting it has to be deliberate.

The x-ray cases in `tests/test_theme_tactics.py` were also split: one test now asserts the
detector fires when the move *creates* the ray, and a new one asserts it stays silent for a ray
that already existed (which the old test had encoded as a hit).

3 new tests; 402 collected, 384 pass and 18 engine tests skip without Stockfish. `ruff` clean.

**Next in the loop**: item 6 — refresh the results surface (README, DATASETS, log), the last
backlog item.

---

## 25. Loop close-out — the data & concepts loop (2026-10-20)

All six backlog items are done and green. This section consolidates what the loop measured and
what it concluded, so the next loop does not have to re-read §20–24.

### Results in one place

| question | result | § |
| --- | --- | --- |
| Do the detectors match independent labels on move-level motifs? | `promotion`, `en_passant`, `smothered_mate`, `double_check` ≈ 1.00; `advanced_pawn` 0.75; `fork` 0.50 | 19 |
| …and on puzzle-level tags? | ≈ 0 — the tag marks the puzzle's *point*, not a per-move fact | 20 |
| Can the classifier learn the tags at all? | macro 0.374 / micro 0.412, against a top-5 baseline of 0.046 / 0.221 | 21, 23 |
| Did symmetry augmentation or an LR schedule help? | No — 0.343 and 0.289 macro against 0.370 plain | 22 |
| Did 2.5× more data help? | No — 0.374 against 0.370, inside noise | 23 |
| Did tightening three broken detectors help F1? | No — false positives −25%/−45%/−11%, F1 flat | 24 |

### The finding

Five independent levers were tried — training longer, augmentation, an LR schedule, 2.5× more
data, and tighter detector definitions — and **none moved macro F1 beyond noise**. The binding
constraint is the **label space**. Lichess tags record which motif is the *point* of a puzzle,
and most motifs are incidental almost everywhere in tactical positions; no amount of training,
data or rule-tightening changes that.

What did work, and is now the default: **per-tag decision thresholds** (macro 0.313 → 0.349,
§21) and **more epochs** (0.349 → 0.370, §22–23). Both are cheap and both were measured.

### What is worth doing next

1. **A label space a per-move model can actually predict** (roadmap M10). The obvious candidate
   is to train on "which move does the puzzle want?" and derive motifs from the solution,
   instead of predicting puzzle-level tags from a single position.
2. **A move-quality corpus** (M7) — real Lichess games in a rating band. Needs an engine or the
   eval DB, both excluded by this loop's offline constraint.
3. **A seed sweep** on the classifier: the remaining ±0.03 macro differences are single-run, and
   the loop repeatedly had to say "inside noise". Three seeds would make those claims decidable.

### Loop hygiene

Every item landed green: 402 tests collected, 384 pass, 18 engine tests skip without Stockfish;
`ruff check` and `ruff format --check` clean; one `experiments/log.csv` row per iteration; one
PROGRESS section per item. The fixture (`tests/data/puzzles_sample.csv`) and the two results CSVs
are committed artefacts, so every number in §20–24 can be re-derived offline.
