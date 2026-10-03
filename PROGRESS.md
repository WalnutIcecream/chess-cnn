# Chess Move Explainer — Progress & Status Report

> Auto-generated status snapshot. Last updated: 2026-10-03.

## 1. Project overview

**Goal:** a system that explains the *intent, tactical importance, and positional effect* of
a chess move. Three layers, built in order:

1. **Symbolic layer** (Stages 1–2): Stockfish measures how good/critical a move is; hand-written
   `python-chess` rules detect tactical + positional themes and derive intent tags. Output is a
   structured `MoveReport` per move.
2. **Dataset layer** (Stage 3): run the symbolic layer at scale over sampled positions to produce
   a weakly-supervised labelled dataset.
3. **Learning layer** (Stages 4–5): a neural net predicts the labels from the board alone, then an
   LLM turns verified reports into prose.

**Repo:** `/home/walnut/chess-ai` (Python 3.11+, package `moveexp`).

**Environment used for this work:**
- Python 3.13 venv: `/tmp/opencode/venv`
- Stockfish 19 (built from source): `/tmp/opencode/stockfish/src/stockfish`
  (the nixpkgs Stockfish 18 build is unreliable and must not be used)
- Lint/format: `ruff`

---

## 2. Status at a glance

| Metric | Value |
| --- | --- |
| Milestones complete | **M1 ✅  M2 ✅** (M3–M10 pending) |
| Test suite | **279 passed** (with Stockfish); engine tests auto-skip without it |
| Lint / format | `ruff check` clean, `ruff format --check` clean |
| Theme detectors registered | **40** |
| Static intent detectors | **9** (+ 2 engine-backed threat tags, opt-in) |
| Frozen vocabularies | 40 themes · 11 intents · 8 quality labels |
| Line coverage of the brief | Sections 5–6 (Stages 1–2) implemented; Sections 8–11 (Stages 3–5) not started |

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
