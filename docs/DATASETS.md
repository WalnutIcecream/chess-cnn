# Datasets

A survey of the public corpora that could feed this project, what each one gives us, and what
we chose. Written after a deliberate search, because the first trained artifact ran on 40
self-play games -- a dataset that measures whether a network can imitate *our own* rules,
which is not the question the project is asking.

## What the project needs

| Need | Wants | Independent of our code? |
| --- | --- | --- |
| Tactic concepts (fork, pin, ...) | moves labelled with the motif, ideally human-curated | **yes** -- otherwise we benchmark our rules against our rules |
| Move quality | positions labelled with how good each move is | yes |
| Positions to encode | FEN + the played move, at scale | n/a |

"Independent" is the whole difficulty. The symbolic layer can generate as many labels as we
like, but they carry no information about whether the rules are *right*. Every source below
was judged first on whether it gives us a label we did not produce.

## Chosen: Lichess puzzle database

`https://database.lichess.org/lichess_db_puzzle.csv.zst` -- **CC0**, ~350 MB compressed.

- **6,157,341** puzzles, rated and tagged (as of the 2026-10-05 export).
- Columns: `PuzzleId, FEN, Moves, Rating, RatingDeviation, Popularity, NbPlays, Themes,
  GameUrl, OpeningTags, DailyDate`.
- `Moves` is UCI; the first move is the opponent's blunder that *creates* the puzzle and the
  rest is the solution. Every solver move is an only-move.
- `Themes` is the prize: Lichess generates tags automatically and then refines them with
  player votes, so they are human-curated ground truth. `fork`, `pin`, `skewer`,
  `discoveredAttack`, `attraction`, `clearance`, `intermezzo`, `quietMove`, `zugzwang`,
  `smotheredMate`, and dozens more. The full list lives in Lichess's
  `translation/source/puzzleTheme.xml`.
- Puzzle generation: Lichess re-analysed 600M games with Stockfish NNUE at 40 Mnodes and
  spent >100 CPU-years producing them.

**Why it wins:** it is small, CC0, already tagged, and its labels are exactly the concepts
this project's detectors claim to find. It powers both the concept dataset
(`scripts/build_puzzle_dataset.py`) and the detector benchmark (`eval/puzzle_benchmark.py`),
so a detector's precision/recall is measured against something we did not write.

Mapped into the project by `moveexp.data.puzzle_themes`; only the tactic tags are used
(phase/length/strength tags like `opening`, `short`, `crushing` describe the game, not the
move, and are dropped).

### What the tags actually measure

The split in `moveexp.data.puzzle_themes` is by **decidability**, and the benchmark reports the
two groups separately:

- **move-level** (19 tags) — decidable from one position and its move.
- **puzzle-level** (9 tags) — true of the whole solution (`kingsideAttack`, `quietMove`,
  `attraction`, …).

Measured on 20,000 puzzles: move-level macro F1 **0.407** against puzzle-level **0.146**
(PROGRESS §20), which is the gap the split exists to expose.

The loop then found a **second, stronger requirement that decidability does not capture**: a tag
is only applied when the motif is *the point of the puzzle*, and most motifs are incidental
almost everywhere in tactical positions. Only the near-deterministic ones clear that bar —
`promotion`, `en_passant`, `smothered_mate`, `double_check` (F1 ≈ 1.00) and `advanced_pawn`
(0.75). `x_ray`, `interference` and `hanging_piece` are perfectly *decidable*, yet score ≈ 0,
because a position containing an x-ray is not a position *about* an x-ray. Tightening their
definitions cut false positives by 11–45% and left F1 flat (PROGRESS §24) — that is what settled
it.

So the benchmark does two jobs: it says which detectors are trustworthy, and it separates "our
rule is wrong" from "this label was never a fair target for a per-move rule".

### What the built dataset looks like

`scripts/build_puzzle_dataset.py --n 200000 --all-solver-moves` produces **299,986 rows** over 27
of the 54 themes, after dropping 708 duplicate positions. Composition: 56% move-only, 23%
puzzle-only, 21% both; rating bands <1200 27%, 1200–1599 23%, 1600–1999 22%, 2000–2399 17%,
2400+ 10%. The builder prints all of this itself, so the numbers here can be re-derived rather
than trusted. See `eval/puzzle_benchmark.py` and `PROGRESS.md` §19–24.

## Considered and deferred

### Lichess evaluation database

`lichess_db_eval.jsonl.zst` -- **CC0**, very large (100+ GB compressed).

- **416,442,401** positions with Stockfish evaluations (2026-10-05), one JSON object per line:
  `{fen, evals:[{pvs:[{cp, mate, line}], knodes, depth}]}`.
- The engine evals are free -- no local Stockfish needed to label a position, which is a big
  deal on a CPU-only box.
- **Deferred** on size: it dwarfs the puzzle corpus by two orders of magnitude. It is the
  obvious next source, and the natural one for a large move-quality corpus, once we are ready
  to stream it rather than store it.

### Lichess monthly game exports

`standard/lichess_db_standard_rated_YYYY-MM.pgn.zst` -- **CC0**, one file per month.

- Real rated games (headers include both players' ratings and the result). Size varies by
  month from tens to hundreds of MB.
- This is what a *real* move-quality corpus should be built from: sample games in a rating
  band, skip opening plies, keep a share of non-quiet positions (the constants for all of
  this already exist in `config.py`: `DEFAULT_RATING_MIN/MAX`, `DEFAULT_SKIP_OPENING_PLIES`,
  `DEFAULT_FLAGGED_SHARE`), then label with a local Stockfish via `moveexp batch`.
- **Deferred**: needs a Stockfish binary and labelling compute. Out of scope for the
  puzzle-first milestone; it is the next one.

### Mirrors and ML-ready variants of the eval database

Useful when the raw JSONL is awkward to stream. All derive from Lichess's CC0 export, but
check each one's licence and schema before use.

| Source | Size / shape |
| --- | --- |
| HuggingFace `Lichess/chess-position-evaluations` | the eval DB as a dataset |
| Kaggle `lichess/chess-evaluations` | 342,059,879 positions; de-normalised to 844,812,067 rows |
| HuggingFace `mateuszgrzyb/lichess-stockfish-normalized` | 316,072,343 deduplicated, ML-ready positions |
| GitHub `r2dev2/ChessData` | in-progress, ~13M evaluations at time of writing |
| Kaggle `christofferbrandt/stockfish-position-evaluations` | Stockfish 18 at depth 12, smaller and consistent |

### Rejected

- **Self-play corpora** for training: they are what caused the original problem -- labels from
  our own rules, and a tiny, unrepresentative position distribution. Still fine as a smoke
  test for the pipeline, not as a dataset.
- **chess.com / FICS bulk data**: no comparable public, licensed, tagged export.

## How the puzzle data is used

```bash
python scripts/download_data.py puzzles                     # ~350 MB -> data/raw/
python eval/puzzle_benchmark.py --puzzles data/raw/lichess_db_puzzle.csv.zst --n 20000
python scripts/build_puzzle_dataset.py --n 200000           # -> data/processed/puzzles.parquet
python scripts/train_concepts.py --labels data/processed/puzzles.parquet
```

## Sources

- [lichess.org open database](https://database.lichess.org/) -- puzzle/eval/game export formats, counts and licences
- [Lichess puzzle theme list (`puzzleTheme.xml`)](https://github.com/lichess-org/lila/blob/master/translation/source/puzzleTheme.xml)
- [Lichess puzzle generator](https://github.com/ornicar/lichess-puzzler)
- [HuggingFace `Lichess/chess-position-evaluations`](https://huggingface.co/datasets/Lichess/chess-position-evaluations)
- [Kaggle `lichess/chess-evaluations`](https://www.kaggle.com/datasets/lichess/chess-evaluations)
- [HuggingFace `mateuszgrzyb/lichess-stockfish-normalized`](https://huggingface.co/datasets/mateuszgrzyb/lichess-stockfish-normalized)
- [GitHub `r2dev2/ChessData`](https://github.com/r2dev2/ChessData)
- [Kaggle `christofferbrandt/stockfish-position-evaluations`](https://www.kaggle.com/datasets/christofferbrandt/stockfish-position-evaluations)
