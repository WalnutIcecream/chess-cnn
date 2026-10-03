# moveexp — Chess Move Explainer

Turns a single played chess move into a **symbolic, auditable** report: what the move was
worth (win probability), how critical the position was, and — later — which tactical theme
it belonged to and what the player's intent plausibly was. The output is a
`MoveReport` dataclass / JSON document designed to be a *training record*, not prose.

Milestone status: **M2 done** (the full symbolic layer — SEE, tactical/material/
king-safety/structure/activity theme detectors, positional features, intent tags, the
`MoveReport` pipeline, and the `analyze-pgn` / `batch` CLI). The dataset builders
(Stage 3) and the neural/LLM stages are not implemented yet — see [Roadmap](#roadmap).

---

## Quick start

Requires Python ≥ 3.11 and a Stockfish binary.

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'

# point the tool and the test-suite at a Stockfish binary
export STOCKFISH_PATH=/path/to/stockfish        # or rely on `stockfish` on PATH

# a mate in one, fully labelled and cached
moveexp --engine-path "$STOCKFISH_PATH" analyze-move \
    --fen "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 4 4" \
    --move "Qxf7#" --depth 18 --multipv 5

moveexp vocab      # print the frozen label vocabularies
```

Global options (`--engine-path`, `--threads`, `--hash`) come **before** the subcommand;
per-search options (`--depth` / `--nodes`, `--multipv`, `--cache-db`, `--no-cache`,
`--out`, `--pretty/--compact`) come **after** it.

```bash
pytest                       # everything; engine tests skip without a binary
pytest -m engine             # only the tests that really start Stockfish
ruff check . && ruff format --check .
```

---

## Layout

```
src/moveexp/
  config.py            all thresholds, paths and frozen vocabularies in one place
  schema.py            LineInfo / QualityInfo / MoveReport / GameReport + Parquet flattening
  engine/
    client.py          StockfishClient: process lifecycle, MultiPV parsing, crash recovery
    cache.py           WAL SQLite analysis cache (FEN + limit signature + MultiPV)
    eval_utils.py      the ONLY place where an evaluation changes sign
  analysis/
    move_quality.py    win-probability loss -> best/excellent/good/inaccuracy/mistake/blunder
    criticality.py     only-move, sharpness, forcing, is_critical
    see.py             static exchange evaluation (capture quality, sacrifice)
    features.py        PositionalDelta: material/mobility/king-safety/pawns/space/activity
    themes/
      base.py          ThemeHit, DetectionContext, the detector registry
      tactics.py       fork/pin/skewer/x-ray/discovered/double-check/hanging/back-rank/...
      material.py      capture/sacrifice/trade/simplification/promotion(-threat)
      king_safety.py   exposes/shelters/weakens-opponent king
      structure.py     passed/isolated/doubled/backward pawns, islands, breaks
      activity.py      outpost/rook files/rook seventh/bishops/development/centre
      intent.py        IntentTag + static intent rules + null-move threat probes
  pipeline.py          assemble a full MoveReport (and a GameReport per game)
  cli.py               analyze-move / analyze-pgn / batch / vocab
tests/                 276 tests; engine tests are marked `engine`
eval/puzzle_benchmark.py   detector precision/recall vs Lichess puzzle tags
data/{raw,cache,processed,audit}/   git-ignored working directories (.gitkeep kept)
```

`data/` is deliberately empty: no corpora are downloaded by the library. Every future
long-running job (game downloads, bulk labelling, dataset builds) will be a standalone,
resumable script under `scripts/` with progress logging and a runtime estimate — never
something you have to run inside an interactive session.

---

## The report

```jsonc
{
  "ply": 0,
  "fen_before": "...", "move_uci": "f3f7", "move_san": "Qxf7#",
  "quality": {
    "label": "best",              // one of QUALITY_LABELS
    "eval_before_cp": 9999.0,     // mover's POV, mate folded in
    "eval_after_cp": 9999.0,
    "win_prob_before": 1.0,       // mate is a certainty, not the saturated 0.996
    "win_prob_after": 1.0,
    "loss_cp": 0.0, "loss_wp": 0.0,
    "best_move": "f3f7", "best_move_cp": 9999.0, "best_move_wp": 1.0,
    "rank": 1, "n_lines": 5, "played_in_multipv": true,
    "is_only_move": true, "gap_to_second_wp": 0.0,
    "sharpness": 0.48, "is_forcing": true, "is_critical": true
  },
  "themes": [
    {"theme": "capture", "squares": ["f3", "f7"], "pieces": ["Q@f7"],
     "confidence": 1.0, "evidence": "takes the p@f7"},
    {"theme": "back_rank_mate", "squares": ["f7", "e8"], "pieces": ["Q@f7"],
     "confidence": 1.0, "evidence": "Qxf7# mates: ..."}
  ],
  "positional_delta": {"material": 100, "mobility": 0, "king_safety": 0,
                        "pawn_structure": 0, "space": 0, "activity": 0},
  "intent": [{"tag": "attacks_king", "evidence": "Qxf7# gives check",
              "moves": [], "confidence": 1.0}],
  "pv": ["f3f7"], "fen_after": "...",
  "meta": { "engine_path": "...", "engine_id": "Stockfish 19", "limit_signature": "d18",
            "depth": 18, "nodes": 349770, "multipv": 5, "tier": 1,
            "cache_hit": false, "dataset_version": "v1" }
}
```

### Perspective rule (the one invariant that matters)

Stockfish scores are always relative to the **side to move**, and so is every `LineInfo`
this project produces (`LineInfo.turn` records whose turn it is). Conversion to any other
point of view happens in exactly one function,
`eval_utils.lines_to_mover_perspective(lines, mover)`, and the *mover's* point of view is
what move quality uses. After a conversion the MultiPV rank order **reverses**, so ranking
helpers order by value (`best_line`), never by `multipv_rank`. `tests/test_eval_utils.py`
and the mirrored-position engine test pin this down.

### Numbers and their formulas

| quantity | definition |
| --- | --- |
| `score_cp` | centi-pawn score from the side to move; mate scores are **not** stored here |
| `mate` | raw mate distance in Stockfish units, sign from the mating side |
| `line_eval_cp(line)` | `score_cp` if present, else `±(MATE_CP_BASE - n)` with `MATE_CP_BASE = 10000` |
| `win_prob` | `1 / (1 + exp(-0.00368208 · cp))` on cp clamped to ±1500; a forced mate is exactly `1.0` / `0.0` |
| `loss_cp` | `max(0, eval_best − eval_played)` |
| `loss_wp` | `max(0, win_prob_best − win_prob_played)` |

Quality labels are exclusive upper bounds on `loss_wp`:

| label | `loss_wp` |
| --- | --- |
| best | rank 1, or `< 0.005` |
| excellent | `< 0.02` |
| good | `< 0.05` |
| inaccuracy | `< 0.10` |
| mistake | `< 0.20` |
| blunder | `≥ 0.20` |

`great` and `brilliant` are **not** applied automatically: they need evidence that does not
exist until Stage 2 (SEE confirmation of a sacrifice). `classify_special()` implements the
rules and takes `sacrifice_confirmed`, which the bulk labeller passes as `False`.

---

## Engine and cache notes

* `StockfishClient` copies every board it searches, so caller state can never be corrupted.
* A crashed/hung engine is restarted **once** (`ENGINE_RESTART_ATTEMPTS = 2` attempts total)
  and the query is retried; a second failure raises `EngineCrashedError`.
* Terminal **and illegal** positions are rejected before the engine sees them. This is not
  pedantry: Stockfish 18 segfaults on an impossible position where the side not to move is
  in check, and Stockfish 19 prints `CRITICAL ERROR` and then stops reading commands.
* python-chess cannot put a timeout on `analyse()`, so a wall-clock safety net
  (`ENGINE_QUERY_TIMEOUT_S = 600 s`) is passed to the engine as part of the limit. It is
  *not* part of `AnalysisLimit.signature`, so it never fragments the cache.
* The cache key is `normalized FEN | engine version | limit signature | MultiPV`; the engine
  version is included so results from different Stockfish builds never collide. Halfmove/
  fullmove counters are dropped because they cannot change the evaluation. SQLite runs in
  WAL mode with a 30 s busy timeout, so several labelling workers can share one file.
  Corrupt rows are treated as misses and deleted rather than aborting a run.
* Every report carries an `EngineProvenance` record — engine name/author (from the UCI
  handshake, not config), limit type and value, MultiPV, Threads, Hash, and the `moveexp`
  version — so labels from different engines or settings are never silently compared. It is
  flattened into `prov_*` columns in Parquet.
* Cost: a depth-16 single-PV search is a few milliseconds; `--multipv 3` roughly doubles
  it. Only positions *not* covered by the MultiPV set need the second ("after") search,
  which `analyse_pair()` skips whenever possible.
* Intent threat tags (`creates_threat` / `parries_threat`) come from null-move engine probes:
  up to **four extra single-PV searches per position**, so they are **off by default** and
  gated by `--null-move-probes` (or `null_move_probes=True` in the pipeline). Run them only
  on positions flagged critical / forcing / theme-bearing, at the reduced
  `NULL_MOVE_PROBE_DEPTH = 10`.

---

## Assumptions and open questions

1. **Mate units.** python-chess reports Stockfish mate scores in its own unit (moves for the
   UCI output). We store the number raw and use it only as a magnitude — never converting it
   to a ply count. `FORCING_MATE_MAX_UNITS = 3` therefore means "mate within ~3 of its own
   units"; if we later want plies, the conversion belongs in `eval_utils`.
2. **Thresholds are a starting point.** The bands in `config.py` are the classic
   lichess-style numbers; they are all in one module so they can be re-tuned against a
   labelled sample without touching logic.
3. **Fixed depth vs node budget.** `--depth` is for careful interactive analysis; a node
   budget (`AnalysisLimit.by_nodes`) costs the same everywhere and is what bulk labelling
   should use for reproducibility.
4. **`themes`, `positional_delta`, `intent` are empty at M1** by design; `PositionalDelta`
   is already part of the schema and flattened for Parquet.
5. **Corpora are out of scope for the library.** No network access from `src/moveexp`.

---

## Roadmap

| milestone | contents |
| --- | --- |
| M1 ✅ | repo layout, config/schema, engine client + cache, eval utilities, move quality, criticality, `analyze-move` CLI, tests |
| M2 ✅ | symbolic layer: SEE, theme detectors (tactics/material/king-safety/structure/activity), positional features, intent rules, `pipeline.py`, `analyze-pgn`/`batch` CLI, puzzle benchmark |
| M3 | data acquisition: resumable downloader + streaming `.zst` readers (PGN / puzzle CSV / eval DB) |
| M4 | sampling, dedupe, oversampling and game-level train/val/test splits |
| M5 | resumable two-tier bulk labelling, label audit and dataset statistics |
| M6 | neural model (multi-label themes + intent, quality head) |
| M7 | LLM explanation layer + verifier, checked against the symbolic reports |

## Licence / attribution

Stockfish is GPL-3.0 and is **not** vendored: point `STOCKFISH_PATH` (or PATH) at your own
build. This project only speaks UCI.
