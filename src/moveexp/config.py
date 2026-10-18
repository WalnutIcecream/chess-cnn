"""Central configuration: paths, engine defaults, vocabularies and every threshold.

Design rules for this module:

* No I/O, no mutable module state. Every constant is a plain immutable value so
  that importing this module from a library is free and tests can compare against
  it without side effects.
* Every magic number used anywhere in the project lives here, with a comment
  stating what it means, its unit and (where possible) why it was chosen.
* Anything that is a *policy* choice (quality label boundaries, criticality
  thresholds, vocabularies) is overridable per call by passing an explicit
  argument; the constants here are only the defaults.

Environment variables
---------------------
``MOVEXP_DATA_DIR``
    Overrides the location of the ``data/`` directory (default: ``<repo>/data``).
``STOCKFISH_PATH``
    Default engine executable used when neither the CLI nor the caller sets one.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Final

# --------------------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------------------

#: Repository root, i.e. the directory that contains ``pyproject.toml`` and ``src/``.
#: ``src/moveexp/config.py`` -> parents[0]=moveexp, [1]=src, [2]=repo root.
PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parents[2]

#: Root of the data directory. Overridable so cloud jobs can point at a fast disk.
DATA_DIR: Final[Path] = Path(os.environ.get("MOVEXP_DATA_DIR", PROJECT_ROOT / "data"))

#: Downloaded PGN / puzzle-CSV / eval-DB files (git-ignored, very large).
RAW_DIR: Final[Path] = DATA_DIR / "raw"
#: SQLite engine cache (git-ignored).
CACHE_DIR: Final[Path] = DATA_DIR / "cache"
#: Sampled positions, labelled Parquet shards, model checkpoints (git-ignored).
PROCESSED_DIR: Final[Path] = DATA_DIR / "processed"
#: Markdown dumps for manual label review (git-ignored).
AUDIT_DIR: Final[Path] = DATA_DIR / "audit"

#: Default SQLite cache file. Shared by every worker process (WAL mode).
DEFAULT_CACHE_DB: Final[Path] = CACHE_DIR / "engine_cache.sqlite3"

#: Version tag written into every labelled row. Bump it whenever the label
#: definition changes, so old and new shards can never be silently mixed.
#: v2 appends the puzzle-tag tactics to ``THEME_VOCAB`` (see themes/tactics_ext.py), so a
#: v1 row decoded against the v2 vocabulary would be misaligned; the bump forces a relabel.
DATASET_VERSION: Final[str] = "v2"

# --------------------------------------------------------------------------------------
# Engine defaults
# --------------------------------------------------------------------------------------

#: Default UCI executable. ``chess.engine.SimpleEngine.popen_uci`` resolves it via PATH.
DEFAULT_ENGINE_PATH: Final[str] = os.environ.get("STOCKFISH_PATH", "stockfish")

#: UCI ``Hash`` in MiB. 256 MiB is plenty for depth <= 18 at MultiPV 3 and keeps the
#: cache file small; raise it when labelling with several threads per process.
DEFAULT_HASH_MB: Final[int] = 256

#: UCI ``Threads``. Default 1: Stage 3 runs one engine *process* per worker, so
#: threads-per-process > 1 would oversubscribe the machine.
DEFAULT_THREADS: Final[int] = 1

#: Carefulness depth used by the interactive CLI and by ``analysis/*.py`` defaults.
DEFAULT_DEPTH: Final[int] = 16

#: Node-limited alternative to depth. Useful for reproducible bulk labelling: a node
#: budget costs the same everywhere, whereas depth cost varies hugely with position.
DEFAULT_NODES: Final[int | None] = None

#: Default MultiPV width. 3 gives a usable "second best" for criticality while staying
#: roughly 1.5-2x the cost of single PV.
DEFAULT_MULTIPV: Final[int] = 3

#: Seconds to wait for the engine to start / answer before treating it as crashed.
ENGINE_START_TIMEOUT_S: Final[float] = 60.0
ENGINE_QUERY_TIMEOUT_S: Final[float] = 600.0

#: How many times the client restarts a crashed engine before giving up.
ENGINE_RESTART_ATTEMPTS: Final[int] = 2

#: Seconds a worker waits for the SQLite lock before raising ``sqlite3.OperationalError``.
CACHE_BUSY_TIMEOUT_S: Final[float] = 30.0

# --------------------------------------------------------------------------------------
# Stage 3 / Stage 4 analysis budgets (see README "Cost model")
# --------------------------------------------------------------------------------------

#: Tier-1 (bulk) depth: first pass over every sampled position.
BULK_DEPTH: Final[int] = 12
#: Tier-1 node budget used when ``BULK_USE_NODES`` is set instead of depth.
BULK_NODES: Final[int] = 300_000
#: Tier-2 (re-analysis) depth for positions flagged critical / forcing / theme-bearing.
DEEP_DEPTH: Final[int] = 18
#: MultiPV for bulk labelling. 3 is the sweet spot: enough for "only move" detection,
#: cheap enough that MultiPV 5 would cost ~1.7x more for labels we barely use.
BULK_MULTIPV: Final[int] = 3
#: Depth for optional null-move threat probes (Stage 2 intent layer).
NULL_MOVE_PROBE_DEPTH: Final[int] = 10

# --------------------------------------------------------------------------------------
# Evaluation <-> win-probability conversion
# --------------------------------------------------------------------------------------

#: Logistic scale in the Stockfish/Lichess win-probability model:
#: ``P(win) = 1 / (1 + exp(-scale * cp))``. This is the widely used value that
#: reproduces lichess win-percentage from Stockfish centipawns.
WIN_PROB_CP_SCALE: Final[float] = 0.00368208

#: Centipawns are clamped to +/- this before the logistic. Without clamping, +2000cp maps
#: to P=0.9998 and the loss_wp buckets for good moves collapse into float noise.
WIN_PROB_CP_CLAMP: Final[float] = 1500.0

#: Centi-pawn value assigned to a mate, used to fold mate scores into the same cp scale:
#: "mate in N" -> +MATE_CP_BASE - N, "mated in N" -> -MATE_CP_BASE + N.
#: 10000 sits far above any real cp score, so a forced mate always dominates.
MATE_CP_BASE: Final[int] = 10_000

# --------------------------------------------------------------------------------------
# Move quality labels (Section 5.5)
# --------------------------------------------------------------------------------------

#: ``loss_wp`` = (win prob of the best move) - (win prob of the played move), clamped at 0.
#: Thresholds are *exclusive upper bounds* on ``loss_wp`` for the label that follows.
#: These are the classic lichess-style bands: 0.005 is roughly "identical eval",
#: 0.02 ~ a pawn-edge of inaccuracy, 0.20 ~ losing a piece.
QUALITY_LOSS_WP_THRESHOLDS: Final[Mapping[str, float]] = MappingProxyType(
    {
        "best": 0.005,
        "excellent": 0.02,
        "good": 0.05,
        "inaccuracy": 0.10,
        "mistake": 0.20,
        "blunder": float("inf"),
    }
)

#: Canonical label order, worst to best. Used for the classification loop and as the
#: class order of the neural model's quality head (softmax index order).
QUALITY_LABELS: Final[tuple[str, ...]] = (
    "blunder",
    "mistake",
    "inaccuracy",
    "good",
    "excellent",
    "best",
    "great",
    "brilliant",
)

#: Labels produced by ``analysis.move_quality.assess_move``; ``great``/``brilliant`` are
#: added afterwards by ``classify_special`` because they need extra evidence.
CORE_QUALITY_LABELS: Final[tuple[str, ...]] = QUALITY_LABELS[:6]

#: A move is "best" if it is rank 1 *or* costs less than this much win probability.
QUALITY_BEST_RANK: Final[int] = 1

#: Optional ``great``: rank 1 and the second-best line loses at least this much win
#: probability relative to the best line (i.e. it is genuinely the only good move).
GREAT_WIN_PROB_SWING: Final[float] = 0.15

#: Optional ``brilliant``: the position before the move must be unclear, otherwise a
#: trivial winning sacrifice would be labelled brilliant.
BRILLIANT_WIN_PROB_CEILING: Final[float] = 0.90

# --------------------------------------------------------------------------------------
# Criticality (Section 5.6)
# --------------------------------------------------------------------------------------

#: Gap (win-prob) between the best and the second-best line above which the best move
#: counts as "the only move". 0.15 ~ 3 pawns of eval or a clearly missed tactic.
ONLY_MOVE_GAP_WP: Final[float] = 0.15

#: Spread of win probability across all MultiPV lines (max - min) above which the
#: position is considered tactically volatile.
CRITICAL_SHARPNESS: Final[float] = 0.30

#: Absolute win-probability change caused by the played move above which the move is
#: called critical even if the engine still stands slightly better afterwards.
CRITICAL_WIN_PROB_CHANGE: Final[float] = 0.10

#: A best-line mate score at or below this number of "mate units" (see
#: ``eval_utils.mate_to_cp``) marks a forced mate, which makes the move forcing.
FORCING_MATE_MAX_UNITS: Final[int] = 3

#: Search horizon (in the PV, from the position after the move) used by the
#: back-rank-mate detector in Stage 2.
BACK_RANK_MATE_MAX_PLIES: Final[int] = 6

# --------------------------------------------------------------------------------------
# Vocabularies (frozen label spaces -- Section 7)
# --------------------------------------------------------------------------------------

#: Stable, ordered theme vocabulary. Multi-hot dataset vectors use exactly this order,
#: so entries may only ever be APPENDED (and the DATASET_VERSION bumped) -- never
#: reordered or removed, or previously written shards decode to the wrong labels.
THEME_VOCAB: Final[tuple[str, ...]] = (
    # -- tactics (themes/tactics.py) -------------------------------------------------
    "fork",  # moved piece hits 2+ valuable targets and survives
    "pin",  # absolute (by is_pinned) or relative pin
    "skewer",  # pinned piece is the *more* valuable one
    "discovered_attack",  # moving reveals an attack that already existed
    "discovered_check",  # moving reveals a check
    "double_check",  # the move checks and also discovers a check
    "hanging_piece",  # an undefended enemy piece becomes attackable
    "threat_created",  # the move leaves a concrete threat against the opponent
    "hanging_piece_defended",  # the move removes a real attack on one of our pieces
    "back_rank_mate",  # forced mate / back-rank weakness
    "trapped_piece",  # a piece that cannot escape and cannot be defended
    "overloaded_defender",  # one piece is the sole defender of two attacked targets
    "deflection",  # lure a defender off a duty
    "interference",  # block a line/knight hop
    "x_ray",  # attack through an enemy piece
    # -- material (themes/material.py) -------------------------------------------------
    "capture",  # material taken by the move
    "sacrifice",  # material given up *and* the eval holds/improves
    "trade",  # even exchange of the two sides' material
    "simplification",  # trade that reduces the number of pieces
    "promotion",  # the move promotes
    "promotion_threat",  # the move leaves a passed pawn one step from promoting
    # -- king safety (themes/king_safety.py) -------------------------------------------
    "exposes_king",  # king safety score got worse for the mover
    "shelters_king",  # king safety score got better for the mover
    "weakens_opponent_king",  # king safety score got worse for the opponent
    # -- pawn structure (themes/structure.py) ------------------------------------------
    "passed_pawn",  # the move leaves the mover with a passed pawn
    "creates_passed_pawn",  # the move itself turns a pawn into a passer
    "isolated_pawn",  # the move leaves the mover with an isolated pawn
    "creates_isolated_pawn",  # the move itself creates the isolation
    "doubled_pawn",  # the move leaves the mover with a doubled pawn
    "backward_pawn",  # pawn that cannot advance and is not defended
    "pawn_island",  # pawn island count changed
    "pawn_break",  # the move breaks a pawn chain
    # -- activity (themes/activity.py) -------------------------------------------------
    "outpost",  # a knight lands on an uncontested forward outpost
    "rook_open_file",  # rook on a file with no pawns
    "rook_semi_open_file",  # rook on a file with only enemy pawns
    "rook_seventh",  # rook on the opponent's second rank
    "bishop_pair",  # the mover owns both bishops
    "bad_bishop",  # bishop blocked by its own pawns / wrong colour
    "develops_piece",  # minor piece or rook leaves the back rank
    "controls_center",  # move gains central control (d4/e4/d5/e5 area)
    # -- puzzle-tag tactics (themes/tactics_ext.py) ------------------------------------
    # These mirror the Lichess puzzle tag vocabulary so the detectors have an
    # independent, human-curated ground truth to be measured against
    # (see eval/puzzle_benchmark.py and moveexp.data.puzzle_themes). APPEND ONLY.
    "attraction",  # a sacrifice lures an enemy piece onto a losing square
    "clearance",  # the move vacates a square/line a following move needs
    "capturing_defender",  # the move removes the defender of an attacked target
    "intermezzo",  # an in-between move (zwischenzug) before the expected recapture
    "quiet_move",  # the winning continuation is neither a check nor a capture
    "zugzwang",  # every legal reply worsens the opponent's position
    "smothered_mate",  # mate with the king hemmed in by its own pieces
    "en_passant",  # the move captures en passant
    "under_promotion",  # the move promotes to something other than a queen
    "advanced_pawn",  # a far-advanced passed pawn is the point of the move
    "defensive_move",  # the move parries a concrete, statically-visible threat
    "attacking_f2f7",  # the move attacks the f2/f7 square next to the enemy king
    "kingside_attack",  # the move adds pressure on the enemy's kingside
    "queenside_attack",  # the move adds pressure on the enemy's queenside
)

#: Stable, ordered intent vocabulary (Section 6.6). Append-only, like THEME_VOCAB.
INTENT_VOCAB: Final[tuple[str, ...]] = (
    "creates_threat",  # after the move the engine, moving again, finds a big jump
    "parries_threat",  # the move removes the threat the opponent had before
    "improves_piece",  # moved piece ends up on a better square by our features
    "prepares_break",  # move clears the way for a pawn break
    "restricts_opponent",  # removes opponent squares / attacks their pieces
    "trades_defender",  # exchange removes one of our defenders of a target
    "develops",  # piece goes to a more active square and is safe
    "castles",  # the move castles
    "simplifies",  # the move reduces material / piece count
    "attacks_king",  # king zone pressure increases
    "defends_material",  # move makes an attacked piece defensible
)

# --------------------------------------------------------------------------------------
# Piece values (Stage 2: SEE and the material detectors)
# --------------------------------------------------------------------------------------

#: Centi-pawn values used by the *symbolic* layer. Deliberately simple, rounded numbers
#: rather than engine evaluations: SEE and the detectors need a stable, explainable scale
#: that a human can check by hand, and nothing here feeds back into the engine.
PIECE_VALUE_CP: Final[Mapping[str, int]] = MappingProxyType(
    {
        "p": 100,
        "n": 320,
        "b": 330,
        "r": 500,
        "q": 900,
        "k": 0,
    }
)

#: Margin, in centi-pawns, by which a static exchange must *win* before the detector calls
#: it a sacrifice rather than merely an even trade. 30cp is roughly "a bit of pawn
#: structure for free"; below that the outcome is noise.
SACRIFICE_MARGIN_CP: Final[int] = 30

#: A capture is only a "real" sacrifice candidate when the piece given up is worth at
#: least a minor (300cp). Trading a pawn for a pawn is not a sacrifice in any useful sense.
SACRIFICE_MIN_PIECE_CP: Final[int] = 300

# --------------------------------------------------------------------------------------
# Positional feature groups (Stage 2: features.py -> PositionalDelta)
# --------------------------------------------------------------------------------------

#: Mobility/space features are per-piece counts, so a single pawn move in the centre is
#: worth ~1-2 units while a rook swing is worth ~10. The weights below are deliberately
#: coarse: PositionalDelta is a *trend* signal for the LLM layer, not a search term.
FEATURE_WEIGHTS: Final[Mapping[str, float]] = MappingProxyType(
    {
        # material: net material swing in centi-pawns (already in a natural scale)
        "material": 1.0,
        # mobility: sum of pseudo-legal move counts, weight ~1/16 of a pawn
        "mobility": 6.0,
        # king safety: attackers and pawn shield around the mover's own king
        "king_safety": 12.0,
        # pawn structure: doubled/isolated/backward penalty, in centi-pawns
        "pawn_structure": 1.0,
        # space: squares in the centre controlled by the mover's side
        "space": 4.0,
        # activity: centralisation of pieces + outposts + open files
        "activity": 5.0,
    }
)

#: Kings count as attackers of the squares they are adjacent to, but each king may only
#: contribute this much to the attack count of a single square (0 or 1 keeps the count
#: comparable with a bishop/rook).
KING_ATTACK_WEIGHT: Final[float] = 0.5

#: Knight/bishop centrality tables (Manhattan distance to the centre of the board). Used
#: by the activity group; indexed by ``chess.square_distance(square, centre)``.
PIECE_CENTRALITY: Final[Mapping[str, tuple[float, ...]]] = MappingProxyType(
    {
        # by distance to d4/e4/d5/e5 (distance 0..7)
        "n": (4.0, 3.0, 2.0, 1.0, 1.0, 0.5, 0.0, 0.0),
        "b": (3.0, 2.5, 2.0, 1.0, 1.0, 0.5, 0.5, 0.0),
        "r": (0.0, 0.0, 0.5, 1.0, 1.0, 1.5, 2.0, 2.0),
        "q": (1.0, 1.0, 1.5, 2.0, 2.0, 1.5, 1.0, 1.0),
    }
)

#: The four squares that count as "the centre" for space and activity purposes, as
#: algebraic names so that this module stays free of a python-chess import.
CENTRE_SQUARES: Final[tuple[str, ...]] = ("d4", "e4", "d5", "e5")

#: How many ranks deep the king zone extends towards the centre from the king's own rank.
#: The zone is the king's rank +/- this, clamped to the board, and the 3 files around it.
KING_ZONE_RANK_SPAN: Final[int] = 2

#: A minor piece on an outpost must be defended by a pawn (and that pawn undefendable by an
#: enemy pawn) to count as a full outpost. See ``activity.py``.
OUTPOST_REQUIRES_PAWN_DEFENCE: Final[bool] = True

#: ...and it has to be *advanced*: rank index (from the owning side's point of view) at
#: least this high, so rank 4 for White and rank 5 for Black. Without this condition every
#: minor piece behind its own pawns would qualify and "outpost" would mean "any knight".
OUTPOST_MIN_RELATIVE_RANK: Final[int] = 3

#: Chebyshev distance from the enemy king below which a minor piece counts as being
#: "in the zone" for activity purposes.
ACTIVITY_KING_ZONE_DISTANCE: Final[int] = 2

#: Bonuses added to the ``activity`` score by a minor piece that owns an outpost and by a
#: rook on an open or semi-open file. They are on the same scale as ``PIECE_CENTRALITY``,
#: i.e. "worth about one good central square".
OUTPOST_BONUS: Final[float] = 2.0
ROOK_OPEN_FILE_BONUS: Final[float] = 1.0

#: Extra activity for a minor piece standing within ``ACTIVITY_KING_ZONE_DISTANCE`` of the
#: enemy king: not an outpost (no pawn defence involved), just a piece in the fight.
MINOR_KING_ZONE_BONUS: Final[float] = 1.0

#: Pawn structure is scored as a quality, not a penalty: each flaw costs points and each
#: passed pawn adds some, so ``after - before`` is positive when the move improved it.
DOUBLED_PAWN_CP: Final[int] = 20
ISOLATED_PAWN_CP: Final[int] = 15
BACKWARD_PAWN_CP: Final[int] = 20
PASSED_PAWN_BONUS_CP: Final[int] = 25

# --------------------------------------------------------------------------------------
# Theme detector thresholds (Stage 2)
# --------------------------------------------------------------------------------------

#: Minimum centi-pawn value of the *least* valuable fork target for the fork to be real
#: (i.e. fork two pieces of at least knight value, or a queen and anything).
FORK_MIN_TARGET_CP: Final[int] = 300

#: A fork must not be trivially self-defeating: the moved piece must survive the opponent's
#: best immediate answer, i.e. the move's own SEE must not lose more than this.
FORK_MAX_SELF_LOSS_CP: Final[int] = 50

#: Win-probability jump that turns a static "attacked square" into a real threat.
THREAT_MIN_ATTACKERS: Final[int] = 1
"""How many enemy attackers of a valuable piece/king square make it a *threat*."""

#: A piece is "hanging" if it is attacked by the mover's side and this poorly defended:
#: number of attackers minus defenders. 1 means undefended, 2 means only one defender.
HANGING_PIECE_MIN_NET_ATTACKERS: Final[int] = 1

#: Minimum value for a piece to count as "material at stake" for hanging/trapped themes.
HANGING_MIN_PIECE_CP: Final[int] = 300

#: How many plies of opponent replies to simulate when checking whether a moved piece is
#: trapped / whether an attack really is a fork that survives.
TACTIC_REPLY_DEPTH: Final[int] = 2

#: A piece counts as "trapped" only if the mover's attack on it survives this many
#: opponent attempts to escape.
TRAPPED_REPLY_DEPTH: Final[int] = 2

#: Passed pawn qualifies as a "promotion threat" once it is within this many ranks of
#: promotion and its file has no enemy pawn ahead of it.
PROMOTION_THREAT_RANKS: Final[int] = 2

#: Rooks on the opponent's second rank (the "seventh") count as ``rook_seventh`` when the
#: file is open or semi-open; rank index from White's side (6 for White, 1 for Black).
ROOK_SEVENTH_RANKS: Final[tuple[int, ...]] = (6, 1)

#: Bishop colour complexes: a bishop is "bad" when its own pawns block both diagonals out
#: of the opponent's half. Detected structurally, no engine needed.
BAD_BISHOP_MIN_BLOCKED_DIAGONALS: Final[int] = 1

# --------------------------------------------------------------------------------------
# Intent thresholds (Stage 2: themes/intent.py)
# --------------------------------------------------------------------------------------

#: A moved piece counts as "improved" when the sum of its own feature weights (centrality,
#: safety, mobility) rises by at least this much.
INTENT_IMPROVES_PIECE_MARGIN: Final[float] = 2.0

#: Win-probability gain for the mover after their move that counts as a decisive
#: improvement (used by ``improves_piece`` / ``develops`` cross-checks).
INTENT_DECISIVE_WP_GAIN: Final[float] = 0.10

#: The engine must find a *single* reply worth at least this much win probability for the
#: move to have "created a threat".
INTENT_THREAT_REPLY_WP: Final[float] = 0.20

# --------------------------------------------------------------------------------------
# Dataset plumbing (Stage 3)
# --------------------------------------------------------------------------------------

#: Number of null-move engine probes per position when the intent layer is enabled.
#: Each probe is one extra engine call, so the engine cost of a position is roughly
#: (1 + NULL_MOVE_PROBES_PER_POSITION) times the base analysis cost.
NULL_MOVE_PROBES_PER_POSITION: Final[int] = 2

#: A null-move probe must move the win probability by at least this much before we
#: claim the move created (or parried) a threat.
NULL_MOVE_THREAT_WP_JUMP: Final[float] = 0.15

#: Number of positions written per Parquet shard during bulk labelling. 50k rows is
#: ~30-60 MB with the full schema: large enough that write overhead is negligible,
#: small enough that a Ctrl+C loses at most a few seconds of work.
LABEL_SHARD_SIZE: Final[int] = 50_000

#: Game-level split fractions (Stage 3). Positions of one game are correlated, so the
#: split is always done on the game id.
SPLIT_FRACTIONS: Final[Mapping[str, float]] = MappingProxyType(
    {"train": 0.80, "val": 0.10, "test": 0.10}
)

#: Default random seed for every sampling / split decision.
DEFAULT_SEED: Final[int] = 20240917

#: First N plies of a game are skipped during sampling: opening positions repeat
#: thousands of times and would dominate the dataset.
DEFAULT_SKIP_OPENING_PLIES: Final[int] = 10

#: Minimum number of full moves in a game for it to be worth sampling.
DEFAULT_MIN_GAME_MOVES: Final[int] = 20

#: Target share of "flagged" (non-quiet) positions in the final sample. Uniform sampling
#: over real games is ~95% quiet moves, which teaches a model to answer "nothing here".
DEFAULT_FLAGGED_SHARE: Final[float] = 0.30

#: Default rating band for Lichess standard games (both players).
DEFAULT_RATING_MIN: Final[int] = 1600
DEFAULT_RATING_MAX: Final[int] = 2200
