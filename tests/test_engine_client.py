"""Tests that need a real Stockfish binary.

All of them are marked ``engine`` and skip when no binary is found. They cover the parts
that synthetic :class:`LineInfo` objects cannot check: UCI parsing, MultiPV ordering,
budget handling, cache round-trips and -- most importantly -- the perspective rule on
mirrored positions.
"""

from __future__ import annotations

import chess
import pytest

from conftest import mirror_fen
from moveexp.engine.client import AnalysisLimit, EngineError, StockfishClient
from moveexp.engine.eval_utils import (
    cp_to_win_prob,
    line_eval_cp,
    lines_to_mover_perspective,
)

#: White is a rook and a queen up with no compensation.
FEN_WINNING_WHITE = "4k3/8/8/8/8/8/1Q6/4K3 w - - 0 1"  # legal: queen vs king
FEN_WINNING_BLACK = "3rk3/4q3/8/8/8/8/8/4K3 b - - 0 1"


# ----------------------------------------------------------------------------- limits
def test_analysis_limit_rejects_ambiguous_budgets():
    with pytest.raises(ValueError):
        AnalysisLimit(depth=10, nodes=1000)
    with pytest.raises(ValueError):
        AnalysisLimit()
    with pytest.raises(ValueError):
        AnalysisLimit(depth=0)


def test_analysis_limit_signatures_are_distinct_and_short():
    assert AnalysisLimit.by_depth(16).signature == "d16"
    assert AnalysisLimit.by_nodes(300_000).signature == "n300000"
    assert AnalysisLimit(movetime=1.5).signature == "t1.5"
    assert AnalysisLimit.from_any(depth=18).depth == 18
    assert AnalysisLimit.from_any(nodes=1000).nodes == 1000
    assert AnalysisLimit.from_any().depth is not None


def test_the_wall_clock_safety_net_does_not_change_the_signature():
    """The timeout guard must not fragment the cache: it is not part of the semantics."""
    plain = AnalysisLimit.by_depth(16)
    guarded = plain.with_max_seconds(60.0)
    assert guarded.signature == plain.signature == "d16"
    assert guarded.to_uci_limit().time == 60.0
    assert guarded.with_max_seconds(90.0) is guarded
    # A movetime budget is already a wall-clock limit and must not be doubled up.
    timed = AnalysisLimit(movetime=0.5)
    assert timed.with_max_seconds(60.0) is timed
    with pytest.raises(ValueError):
        AnalysisLimit(movetime=0.5, max_seconds=60.0)


# --------------------------------------------------------------------------- searching
@pytest.mark.engine
def test_single_pv_search(engine_client: StockfishClient):
    board = chess.Board()
    lines = engine_client.analyse(board, AnalysisLimit.by_depth(8), multipv=1)
    assert len(lines) == 1
    line = lines[0]
    assert line.depth >= 8
    assert line.nodes > 0
    assert line.turn == chess.WHITE
    assert line.score_cp is not None or line.mate is not None
    assert line.move in {m.uci() for m in board.legal_moves}
    assert line.pv[0] == line.move


@pytest.mark.engine
def test_multipv_returns_ordered_lines(engine_client: StockfishClient):
    board = chess.Board()
    lines = engine_client.analyse(board, AnalysisLimit.by_depth(10), multipv=3)
    assert 2 <= len(lines) <= 3
    assert [line.multipv_rank for line in lines] == list(range(1, len(lines) + 1))
    scores = [line.score_cp for line in lines if line.score_cp is not None]
    assert scores == sorted(scores, reverse=True)
    moves = [line.move for line in lines]
    assert len(set(moves)) == len(moves)


@pytest.mark.engine
def test_node_budget_is_accepted(engine_client: StockfishClient):
    board = chess.Board()
    lines = engine_client.analyse(board, AnalysisLimit.by_nodes(50_000), multipv=1)
    assert lines and lines[0].nodes > 0


@pytest.mark.engine
@pytest.mark.parametrize(
    "fen",
    [
        "r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4",  # Scholar's mate
        "7k/8/6Q1/8/8/8/5K2/8 b - - 0 1",  # stalemate
    ],
)
def test_terminal_position_is_rejected(engine_client: StockfishClient, fen: str):
    board = chess.Board(fen)
    assert board.status() == chess.STATUS_VALID, "the fixture itself must be legal"
    assert board.is_game_over()
    with pytest.raises(EngineError, match="position is over"):
        engine_client.analyse(board, AnalysisLimit.by_depth(6))


def test_illegal_position_is_rejected_before_reaching_the_engine(engine_client: StockfishClient):
    """An impossible position must fail loudly, not segfault the engine (SF 18 does)."""
    board = chess.Board("4k3/8/8/8/8/8/4Q3/3RK3 w - - 0 1")  # white queen already attacks e8
    assert board.status() != chess.STATUS_VALID
    with pytest.raises(EngineError, match="not legal for the engine"):
        engine_client.analyse(board, AnalysisLimit.by_depth(6))
    # The engine must still be usable afterwards.
    assert engine_client.analyse(chess.Board(), AnalysisLimit.by_depth(8))


@pytest.mark.engine
def test_using_the_client_outside_its_context_raises(engine_client: StockfishClient):
    from moveexp.engine.client import EngineNotRunningError

    with pytest.raises(EngineNotRunningError):
        StockfishClient("stockfish-that-does-not-exist").analyse(chess.Board())


# ------------------------------------------------------------------------ perspective
@pytest.mark.engine
def test_mirrored_positions_give_mirrored_evaluations(engine_client: StockfishClient):
    """The same winning position, colours swapped: the mover's advantage is the same.

    Raw engine scores are always relative to the side to move, so in *both* positions the
    mover is winning and the raw score is large and positive. Only after converting to a
    fixed colour (here White) do the two negate each other.
    """
    white = chess.Board(FEN_WINNING_WHITE)
    black = chess.Board(mirror_fen(FEN_WINNING_WHITE))
    limit = AnalysisLimit.by_depth(14)

    white_lines = engine_client.analyse(white, limit, multipv=1)
    black_lines = engine_client.analyse(black, limit, multipv=1)

    # `line_eval_cp` folds mate lines into cp so the test does not depend on whether the
    # engine happened to report a mate score or a large cp score at this depth.
    white_mover_wp = cp_to_win_prob(line_eval_cp(white_lines[0]))
    black_mover_wp = cp_to_win_prob(line_eval_cp(black_lines[0]))
    white_cp = line_eval_cp(white_lines[0])
    assert white_mover_wp > 0.75, "White to move should be winning in this position"
    assert black_mover_wp == pytest.approx(white_mover_wp, abs=0.05), (
        "the mirror is the same position seen by the other side, so the mover's advantage matches"
    )

    # The same search, seen from White's point of view: the sign must flip exactly (that part is
    # pure logic, no engine involved). A fixed-depth search is not perfectly symmetric between
    # a position and its mirror - the engines explore in a colour-dependent order - so the
    # magnitudes are only compared loosely. A real sign error would still show up as a score
    # with the wrong sign, not as a slightly different number.
    mirrored_in_white_pov = lines_to_mover_perspective(black_lines, chess.WHITE)
    black_cp = line_eval_cp(black_lines[0])
    mirrored_cp = line_eval_cp(mirrored_in_white_pov[0])
    assert mirrored_cp == pytest.approx(-black_cp), "conversion flips the sign exactly"
    assert white_cp > 0 and black_cp > 0, "in both positions the side to move is winning"
    assert abs(white_cp - black_cp) <= 400.0, "mirrored evaluations must be close"
    from_white = cp_to_win_prob(mirrored_cp)
    assert from_white < 0.25
    assert white_mover_wp + from_white == pytest.approx(1.0, abs=0.1)


@pytest.mark.engine
def test_mover_perspective_conversion_of_engine_lines(engine_client: StockfishClient):
    """``lines_to_mover_perspective`` is the only place a score changes sign."""
    board = chess.Board(FEN_WINNING_WHITE)
    lines = engine_client.analyse(board, AnalysisLimit.by_depth(12), multipv=2)
    white_pov = lines_to_mover_perspective(lines, chess.WHITE)
    black_pov = lines_to_mover_perspective(lines, chess.BLACK)
    assert white_pov[0].score_cp == pytest.approx(lines[0].score_cp)
    assert black_pov[0].score_cp == pytest.approx(-float(lines[0].score_cp))
    assert all(line.turn is chess.BLACK for line in black_pov)


@pytest.mark.engine
def test_analyse_pair_skips_the_second_search_when_the_move_is_in_multipv(
    engine_client: StockfishClient,
):
    board = chess.Board()
    lines = engine_client.analyse(board, AnalysisLimit.by_depth(10), multipv=3)
    best = lines[0].move
    before, after = engine_client.analyse_pair(
        board, chess.Move.from_uci(best), AnalysisLimit.by_depth(10), multipv=3
    )
    assert after is None
    assert before[0].move == best

    # A move the engine did not list forces the second search.
    unused = next(m for m in board.legal_moves if m.uci() not in {line.move for line in lines})
    before2, after2 = engine_client.analyse_pair(
        board, unused, AnalysisLimit.by_depth(10), multipv=3
    )
    assert after2 is not None and after2[0].turn is chess.BLACK


# ------------------------------------------------------------------------------ cache
@pytest.mark.engine
def test_cache_hit_avoids_a_second_search(stockfish_path: str, cache_db):
    from moveexp.engine.cache import AnalysisCache

    with (
        AnalysisCache(cache_db) as cache,
        StockfishClient(stockfish_path, threads=1, hash_mb=32, cache=cache) as client,
    ):
        board = chess.Board()
        limit = AnalysisLimit.by_depth(10)
        first = client.analyse(board, limit, multipv=2)
        assert client.stats.searches == 1
        second = client.analyse(board, limit, multipv=2)
        assert client.stats.searches == 1, "second call must come from the cache"
        assert client.stats.cache_hits == 1
        assert [line.model_dump() for line in first] == [line.model_dump() for line in second]

        # A different budget is a different key and must be searched.
        client.analyse(board, AnalysisLimit.by_depth(11), multipv=2)
        assert client.stats.searches == 2

        # ... and so is a different position with the same counters.
        client.analyse(board.copy(), limit, multipv=2)
        assert client.stats.searches == 2
        assert cache.stats().hit_rate == pytest.approx(0.5, abs=0.01)


@pytest.mark.engine
def test_cache_survives_reopening(stockfish_path: str, cache_db):
    from moveexp.engine.cache import AnalysisCache, make_cache_key

    board = chess.Board(FEN_WINNING_WHITE)
    limit = AnalysisLimit.by_depth(10)
    with (
        AnalysisCache(cache_db) as cache,
        StockfishClient(stockfish_path, threads=1, hash_mb=32, cache=cache) as client,
    ):
        engine_version = client.engine_id
        expected = client.analyse(board, limit, multipv=1)

    with AnalysisCache(cache_db) as cache:
        key = make_cache_key(board.fen(), limit.signature, 1, engine_version=engine_version or "")
        lines = cache.get(key)
        assert lines is not None
        assert lines[0].score_cp == expected[0].score_cp
        assert lines[0].pv == expected[0].pv


@pytest.mark.engine
def test_cache_can_be_bypassed(stockfish_path: str, cache_db):
    from moveexp.engine.cache import AnalysisCache

    with (
        AnalysisCache(cache_db) as cache,
        StockfishClient(stockfish_path, threads=1, hash_mb=32, cache=cache) as client,
    ):
        board = chess.Board()
        limit = AnalysisLimit.by_depth(8)
        client.analyse(board, limit, multipv=1)
        client.analyse(board, limit, multipv=1, use_cache=False)
        assert client.stats.searches == 2
        assert client.stats.cache_hits == 0


@pytest.mark.engine
def test_restart_recovers_a_stopped_engine(engine_client: StockfishClient):
    """Killing the process behind the client's back must not crash the next query."""
    from moveexp.engine.client import EngineNotRunningError

    board = chess.Board()
    engine_client.analyse(board, AnalysisLimit.by_depth(8))
    engine_client.close()
    assert engine_client.is_running is False
    with pytest.raises(EngineNotRunningError):
        engine_client.analyse(board, AnalysisLimit.by_depth(8))
    engine_client.start()
    lines = engine_client.analyse(board, AnalysisLimit.by_depth(8))
    assert lines[0].depth >= 8
    assert engine_client.engine_id


def test_start_failure_reports_the_path(tmp_path):
    from moveexp.engine.client import EngineNotRunningError

    bogus = tmp_path / "not-an-engine"
    client = StockfishClient(str(bogus))
    with pytest.raises(EngineNotRunningError, match="could not start UCI engine"):
        client.start()
    assert client.is_running is False


# ------------------------------------------------------------------ cache (no engine)
def test_cache_round_trip_without_an_engine(cache_db, line_factory):
    from moveexp.engine.cache import AnalysisCache, make_cache_key

    board = chess.Board()
    key = make_cache_key(board.fen(), "d16", 3)
    lines = [line_factory(move="e2e4", cp=31, rank=1), line_factory(move="d2d4", cp=12, rank=2)]

    with AnalysisCache(cache_db) as cache:
        assert cache.get(key) is None
        cache.put(key, lines, fen=board.fen(), limit_signature="d16", multipv=3)
        cached = cache.get(key)
        assert cached is not None
        assert [line.model_dump() for line in cached] == [line.model_dump() for line in lines]
        assert cache.count() == 1
        assert cache.stats().hits == 1
        assert cache.stats().misses == 1
        assert cache.stats().hit_rate == pytest.approx(0.5)


def test_cache_put_is_idempotent_and_ignores_empty_lines(cache_db, line_factory):
    from moveexp.engine.cache import AnalysisCache, make_cache_key

    board = chess.Board()
    key = make_cache_key(board.fen(), "d16", 3)
    with AnalysisCache(cache_db) as cache:
        cache.put(key, [], fen=board.fen(), limit_signature="d16", multipv=3)
        assert cache.count() == 0
        cache.put(key, [line_factory()], fen=board.fen(), limit_signature="d16", multipv=3)
        cache.put(key, [line_factory(cp=99)], fen=board.fen(), limit_signature="d16", multipv=3)
        assert cache.count() == 1
        assert cache.get(key)[0].score_cp == pytest.approx(99.0)


def test_cache_discards_corrupt_payloads(cache_db, line_factory):
    from moveexp.engine.cache import AnalysisCache, make_cache_key

    board = chess.Board()
    key = make_cache_key(board.fen(), "d16", 3)
    with AnalysisCache(cache_db) as cache:
        cache.put(key, [line_factory()], fen=board.fen(), limit_signature="d16", multipv=3)
        cache._conn.execute("UPDATE analyses SET payload = 'not json'")
        assert cache.get(key) is None
        assert cache.count() == 0
