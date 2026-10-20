# moveexp — data & concepts loop

The previous loop (demo & presentation) finished all four of its items and stopped. This loop
takes over at the point the last iteration reached: the project now has a **real** dataset
(the Lichess puzzle export) and the first honest measurements, and the job is to make those
numbers trustworthy and then better.

Numbers that define the starting line (PROGRESS §19):

- **Detector benchmark** (20k puzzles): move-level motifs score well — `smothered_mate`,
  `en_passant`, `promotion`, `double_check` ≈ 1.00, `advanced_pawn` 0.75, `fork` 0.50 — while
  puzzle-level descriptions score ≈ 0 (`x_ray` 0.00, `interference` 0.00, `hanging_piece` 0.05).
- **Concept classifier**: micro F1 0.436, macro F1 0.313, but **8 tags at 0.00** (one global
  threshold never fires on rare tags) and the prevalence baseline is **degenerate (0.000)**, so
  there is no real bar yet.

## Focus (required)

> Make the measured numbers trustworthy, then make the concept classifier materially better —
> offline, engine-free, and reproducible from `scripts/`.

## Backlog — do ONE item per iteration, in this order

1. **Tag groups + an offline fixture.** Split the mapped tags into move-level (decidable from
   the position) and puzzle-level, in `moveexp/data/puzzle_themes.py`; report both groups in
   `eval/puzzle_benchmark.py` (add a `group` column). Commit a small fixture
   `tests/data/puzzles_sample.csv` (~300 puzzles) so later items can run the benchmark and the
   dataset builder offline — the real corpus is 300 MB and git-ignored.
2. **A real baseline and per-tag thresholds.** Add a top-k prevalence baseline (predict the k
   most common training tags; k tuned on val) so the comparison is not degenerate, and tune one
   threshold *per tag* on val instead of one global threshold. Report the model under both.
3. **Stronger classifier training.** Use the symmetry augmentation already in
   `moveexp.model` (`colour_flip`, `mirror_files`, `augment_planes`) on each training batch,
   add an LR schedule and early stopping on the per-tag val metric. Flags for each ablation;
   default stays CPU-runnable in minutes.
4. **Puzzle dataset upgrade.** `build_puzzle_dataset.py`: all-solver-moves option, dedupe by
   normalised FEN, tag-group and rating-band in the summary; keep the row keys
   `build_puzzle_dataset` reads stable.
5. **Detector precision pass + regression guard.** Rewrite the detectors whose definition is
   simply wrong rather than mismatched (`x_ray`, `interference`, `hanging_piece`,
   king/queenside attack), and pin their F1 on the committed fixture so a re-break fails CI
   offline. Do **not** chase the puzzle-level tags.
6. **Refresh the results surface.** `PROGRESS.md` (new section with the grouped benchmark and
   the ablation table), `README.md`, `docs/DATASETS.md`, `experiments/log.csv`.

## Definition of done

- Each item: tests added/extended and green, one row in `experiments/log.csv`, `PROGRESS.md`
  updated. Never mark an item done while tests fail.
- Loop-wide: the classifier beats the top-k baseline on macro F1; the benchmark reports
  move-level and puzzle-level groups separately; the whole pipeline reruns from
  `scripts/download_data.py` onward against a clean `data/`.

## Each iteration

1. Verify green first: `pytest -q` and `ruff check`. If either is red, fix that before anything
   else.
2. Do exactly ONE backlog item. Run `pytest` and `ruff` before marking it done.
3. Append one row to `experiments/log.csv`; note the change in `PROGRESS.md`.
4. If backlog items remain, schedule the next check with `schedule_wakeup` at the **shortest
   allowed delay (60 seconds)**. Do not back off to minutes: the backlog is a queue to drain,
   not a poll to pace, and a spent iteration should be followed immediately by the next one.
   `schedule_wakeup` replaces any pending check, so the most recent call is the only timer that
   matters. Once all six items are done and green, stop the loop (`schedule_wakeup` with
   `stop: true`) — do not invent work.

## Constraints

- **Offline and engine-free.** No new downloads and no Stockfish: work with the puzzle corpus
  and `data/processed/puzzles.parquet` already on disk. The move-quality corpus (M7) waits for
  a later loop with an engine.
- Add alongside existing code; never modify passing code to make room for a new item.
- Prefer a measurement over a claim: if a detector or tag cannot be measured, say so in
  `PROGRESS.md` rather than tuning it blindly.
- One item per iteration. Small, tested, logged.

## Current state (update as work lands)

- Symbolic layer, explanation layer, demo, data layer, puzzle benchmark and concept classifier
  are all done (PROGRESS §11–19).
- **Backlog item 1 DONE** — tag groups (`MOVE_LEVEL_TAGS` / `PUZZLE_LEVEL_TAGS` and
  `theme_group()`), a grouped benchmark report, and the committed stratified fixture
  `tests/data/puzzles_sample.csv` (540 puzzles, 27/28 themes). Move-level macro F1 0.436 vs
  puzzle-level 0.265 on the fixture; the ordering is asserted in CI (PROGRESS §20).
- **Backlog item 2 DONE** — `top_k_baseline`/`tune_top_k` (a real, non-degenerate bar) and
  `tune_per_tag_thresholds`/`apply_per_tag_thresholds`, with early stopping on per-tag val
  macro F1. Macro F1 0.313 → **0.349** (micro 0.436 → 0.384); every previously-zero tag now
  scores (PROGRESS §21).
- **Backlog item 3 DONE** — symmetry augmentation, a cosine LR schedule and early stopping are
  implemented and ablated (`experiments/concepts_ablation.csv`); both new ideas measured *worse*
  than plain training (macro 0.343 / 0.289 vs 0.370) and are off by default, while longer
  training did help (0.349 → 0.370). See PROGRESS §22 — this is a negative result, recorded
  rather than tuned away.
- **Backlog item 4 DONE** — `dedupe_by_position` (normalised FEN), `rating_band`/`tag_groups`
  columns and a real build summary; rebuilt to **299,986 rows** (2.5×) with
  `--all-solver-moves`. Macro F1 0.370 → 0.374 — inside noise, so dataset size is *not* the
  binding constraint here (label noise is a confound). PROGRESS §23.
- **Backlog item 5 DONE** — `x_ray` is now move-linked (`_opens_ray`), `interference` requires
  the shielded piece to have been threatened, `hanging_piece` means undefended. False-positive
  volume fell 25% / 45% / 11% and move-group micro F1 rose 0.242 → 0.253, but per-theme F1 for
  those three did **not** improve — the tag is applied only when the motif is the puzzle's
  point. Recorded, not chased. The fixture-pinned guard (`DETECTOR_EXPECTATIONS`) uses F1 floors
  **and** detection ceilings so a revert fails offline. PROGRESS §24.
- **Backlog item 6 DONE** — results surface refreshed: a measured-results summary and updated
  roadmap in `README.md`, the caveat in `docs/DATASETS.md` reconciled with what the benchmark
  actually showed, and `PROGRESS.md` §2 + the §25 close-out with the consolidated table.
  PROGRESS §25.

**All six backlog items are complete and green — nothing in this loop remains. Verify green and
stop the loop (`schedule_wakeup` with `stop: true`). Do NOT invent further work.**

## Environment

- NixOS. Run Python inside the project shell so the wheel libs resolve:
  `nix-shell --run '.venv/bin/python ...'` (the `shell.nix` puts `libstdc++`/`zlib`/`zstd` on
  `LD_LIBRARY_PATH`).
- Ruff is not runnable from the venv on NixOS; use `nix-shell -p ruff --run 'ruff check ...'`.
- **Stockfish is not required** for any item in this loop — the detectors are pure
  `python-chess` and the concept classifier trains from puzzle tags.
- Data already present: `data/raw/lichess_db_puzzle.csv.zst` (6.16M tagged puzzles, CC0),
  `data/processed/puzzles.parquet` (299,986 rows, built with `--all-solver-moves`),
  `data/audit/puzzle_benchmark.csv`, `experiments/concepts_ablation.csv`. All git-ignored;
  regenerate with `scripts/download_data.py puzzles`, `scripts/build_puzzle_dataset.py`,
  `eval/puzzle_benchmark.py`.
- CPU only (torch 2.x CPU). Full-corpus runs take minutes; prefer the committed fixture for
  the per-iteration red/green gate.
