"""Tests for the theme layer's shared plumbing (``analysis/themes/base.py``).

The registry is global by design -- importing a detector module is what registers it -- so
these tests restore the registry around the ones that write to it.
"""

from __future__ import annotations

import chess
import pytest

from moveexp.analysis.themes.base import (
    REGISTRY,
    DetectionContext,
    DetectorReport,
    ThemeHit,
    detect,
    detector,
    iter_themes,
    piece_label,
    registered_detectors,
    run_all,
    theme_order,
    validate_theme,
)
from moveexp.config import THEME_VOCAB
from moveexp.schema import ThemeHitModel
from positions import after, board


@pytest.fixture
def clean_registry():
    """Run a test against an empty registry, restoring the global one afterwards.

    Detector modules register themselves on import, so other test modules may already have
    populated the global registry by the time these run. Clearing it here makes the
    registry tests independent of import order.
    """
    saved = list(REGISTRY)
    REGISTRY[:] = []
    try:
        yield REGISTRY
    finally:
        REGISTRY[:] = saved


# ------------------------------------------------------------------------ the vocabulary
def test_vocabulary_is_accepted_and_typos_are_not():
    assert validate_theme("fork") == "fork"
    assert theme_order("fork") < theme_order("capture")
    with pytest.raises(ValueError, match="not in THEME_VOCAB"):
        validate_theme("forkk")
    with pytest.raises(ValueError, match="not in THEME_VOCAB"):
        theme_order("not_a_theme")


def test_a_hit_needs_a_known_theme_evidence_and_sane_confidence():
    with pytest.raises(ValueError, match="not in THEME_VOCAB"):
        ThemeHit("double_knight_take", evidence="...")
    with pytest.raises(ValueError, match="without evidence"):
        ThemeHit("fork", squares=("e5",))
    with pytest.raises(ValueError, match=r"confidence must be in \[0, 1\]"):
        ThemeHit("fork", evidence="...", confidence=1.5)


def test_hits_sort_in_vocabulary_order():
    hits = [
        ThemeHit("sacrifice", evidence="gives up the exchange"),
        ThemeHit("fork", evidence="two targets"),
        ThemeHit("capture", evidence="takes a pawn"),
    ]
    assert [hit.theme for hit in sorted(hits, key=ThemeHit.sort_key)] == [
        "fork",
        "capture",
        "sacrifice",
    ]


def test_hit_serialises_to_the_schema():
    hit = ThemeHit(
        "fork", squares=("e5", "d5"), pieces=("N@f3",), confidence=0.9, evidence="knight hits both"
    )
    model = hit.to_model()

    assert isinstance(model, ThemeHitModel)
    assert model.model_dump() == {
        "theme": "fork",
        "squares": ["e5", "d5"],
        "pieces": ["N@f3"],
        "confidence": 0.9,
        "evidence": "knight hits both",
    }


def test_piece_labels_follow_the_fen_case_convention():
    b = board("wN@f3", "bQ@d5", "wK@e1", "bK@e8")
    assert piece_label(b, chess.parse_square("f3")) == "N@f3"
    assert piece_label(b, chess.parse_square("d5")) == "q@d5"
    assert piece_label(b, chess.parse_square("a4")) == "@a4"


# ---------------------------------------------------------------------------- the context
def test_context_rejects_illegal_moves():
    b = chess.Board()
    with pytest.raises(ValueError, match="not legal"):
        DetectionContext.from_move(b, chess.Move.from_uci("e2e5"))


def test_context_describes_a_quiet_move():
    b = chess.Board()
    ctx = DetectionContext.from_move(b, b.parse_san("e4"))

    assert ctx.side is chess.WHITE
    assert ctx.opponent is chess.BLACK
    assert ctx.board.turn is chess.WHITE and ctx.after.turn is chess.BLACK
    assert ctx.san() == "e4" and ctx.uci() == "e2e4"
    assert ctx.from_square == chess.E2 and ctx.to_square == chess.E4
    assert ctx.moved_piece == chess.Piece.from_symbol("P")
    assert ctx.captured is None and not ctx.is_capture
    assert not ctx.is_check and not ctx.is_mate
    assert not ctx.is_castling and not ctx.is_promotion and not ctx.is_ep
    assert ctx.see.gain_cp == 0
    assert ctx.features_before.side is chess.WHITE and ctx.features_after.side is chess.WHITE


def test_context_describes_a_capture():
    b = board("wN@c3", "bN@d5", "wK@e1", "bK@e8")
    ctx = DetectionContext.from_move(b, b.parse_san("Nxd5"))

    assert ctx.is_capture
    assert ctx.captured == chess.Piece.from_symbol("n")
    assert ctx.see.gain_cp == 320  # an undefended knight is simply won
    assert ctx.pieces(ctx.after, chess.parse_square("d5")) == ("N@d5",)


def test_context_describes_en_passant():
    b = board("wP@e5", "bP@d5", "wK@h1", "bK@h8", "bR@a8", ep="d6")
    ctx = DetectionContext.from_move(b, b.parse_san("exd6"))

    assert ctx.is_capture and ctx.is_ep
    assert ctx.captured == chess.Piece.from_symbol("p")
    assert ctx.captured.color is chess.BLACK
    assert ctx.after.piece_at(chess.parse_square("d6")) == chess.Piece.from_symbol("P")
    assert b.piece_at(chess.parse_square("d5")) == chess.Piece.from_symbol("p")  # input untouched


def test_context_describes_a_promotion():
    b = board("wP@b7", "bR@a8", "wK@h1", "bK@h8")
    ctx = DetectionContext.from_move(b, b.parse_san("bxa8=Q+"))

    assert ctx.is_promotion and ctx.is_check
    assert ctx.moved_piece == chess.Piece.from_symbol("P")
    assert ctx.moved_piece_after == chess.Piece.from_symbol("Q")


def test_context_describes_castling():
    b = after("e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5", "d3", "g6")
    ctx = DetectionContext.from_move(b, b.parse_san("O-O"))

    assert ctx.is_castling
    assert ctx.moved_piece_after == chess.Piece.from_symbol("K")
    assert ctx.to_square == chess.G1


def test_context_does_not_mutate_the_input_board():
    b = chess.Board()
    fen_before = b.fen()
    DetectionContext.from_move(b, b.parse_san("e4"))

    assert b.fen() == fen_before


def test_context_helpers_name_squares_and_pieces():
    b = chess.Board()
    ctx = DetectionContext.from_move(b, b.parse_san("Nf3"))

    assert ctx.squares(chess.E4, chess.D4) == ("e4", "d4")
    assert ctx.pieces(None, chess.F3) == ("@f3",)  # before the move f3 was empty
    assert ctx.pieces(ctx.after, chess.F3) == ("N@f3",)


# ------------------------------------------------------------------------------- registry
def test_registration_is_exclusive_by_name(clean_registry):
    @detector
    def detect_something(ctx: DetectionContext) -> tuple[ThemeHit, ...]:
        return ()

    assert detect_something in registered_detectors()

    with pytest.raises(ValueError, match="already registered"):

        @detector
        def detect_something(ctx: DetectionContext) -> tuple[ThemeHit, ...]:  # noqa: F811
            return ()


def test_run_all_sorts_and_deduplicates(clean_registry):
    ctx = DetectionContext.from_move(chess.Board(), chess.Board().parse_san("e4"))
    duplicate = ThemeHit("fork", squares=("e5",), evidence="same twice")

    hits = run_all(
        ctx,
        [
            lambda c: (duplicate,),
            lambda c: (duplicate,),
            lambda c: (ThemeHit("capture", evidence="x"),),
        ],
    )

    # THEME_VOCAB lists the tactics before the material themes, so "fork" sorts first even
    # though the capture detector ran later.
    assert [hit.theme for hit in hits] == ["fork", "capture"]
    assert next(iter(iter_themes(hits))) == "fork"


def test_detect_runs_the_registry(clean_registry):
    @detector
    def detect_quiet_fork(ctx: DetectionContext) -> tuple[ThemeHit, ...]:
        return (ThemeHit("fork", squares=(chess.square_name(ctx.to_square),), evidence="test"),)

    assert detect(chess.Board(), chess.Board().parse_san("e4"))[0].theme == "fork"


def test_empty_registry_produces_no_hits(clean_registry):
    assert registered_detectors() == ()
    assert detect(chess.Board(), chess.Board().parse_san("e4")) == []


def test_detector_report_groups_by_theme():
    report = DetectorReport(
        (
            ThemeHit("fork", evidence="two targets"),
            ThemeHit("capture", evidence="takes a pawn"),
            ThemeHit("fork", evidence="and again"),
        )
    )

    assert report.themes() == ("fork", "capture")
    assert report.has("fork") and not report.has("pin")
    assert len(report.of("fork")) == 2
    with pytest.raises(ValueError, match="not in THEME_VOCAB"):
        report.of("nope")


def test_every_theme_in_the_vocabulary_is_reachable_as_a_hit():
    """The registry cannot silently shrink: every declared name has to be constructible."""
    for theme in THEME_VOCAB:
        assert ThemeHit(theme, evidence="constructed").theme == theme
