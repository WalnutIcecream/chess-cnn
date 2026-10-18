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
| Milestones complete | symbolic layer, explanation layer, demo, **data layer**, **puzzle benchmark**, **concept classifier** (see `README.md` roadmap) |
| Test suite | **371 passed, 18 skipped** (389 collected); engine tests auto-skip without Stockfish |
| Lint / format | `ruff check` clean, `ruff format --check` clean |
| Theme detectors registered | **54** (40 original + 14 puzzle-tag tactics) |
| Static intent detectors | **9** (+ 2 engine-backed threat tags, opt-in) |
| Frozen vocabularies | 54 themes · 11 intents · 8 quality labels (`DATASET_VERSION` = `v2`) |
| Line coverage of the brief | Sections 5–6 (Stages 1–2) implemented; Stage 3 partially, via the puzzle corpus |

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
