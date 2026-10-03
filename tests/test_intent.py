"""Intent detectors: the static tags plus the model/validation plumbing.

The threat tags (``creates_threat`` / ``parries_threat``) need an engine, so their test is
marked ``engine`` and only checks that the probe runs; the exact engine numbers are not
asserted.
"""

from __future__ import annotations

import chess
import pytest

from moveexp.analysis.themes import register_all
from moveexp.analysis.themes.base import DetectionContext, run_all
from moveexp.analysis.themes.intent import (
    IntentContext,
    IntentTag,
    detect_intents,
    threat_probe,
)
from moveexp.schema import IntentTagModel
from positions import after, board

register_all()  # theme detectors are needed by the theme-derived intents


def _tags(b: chess.Board, san: str) -> set[str]:
    move = b.parse_san(san)
    ctx = DetectionContext.from_move(b, move)
    return {tag.tag for tag in detect_intents(IntentContext.from_detection(ctx, run_all(ctx)))}


# ---------------------------------------------------------------------------- the model
def test_intent_tag_validates_vocabulary_and_evidence():
    with pytest.raises(ValueError, match="not in INTENT_VOCAB"):
        IntentTag("not_an_intent", evidence="x")
    with pytest.raises(ValueError, match="without evidence"):
        IntentTag("develops")
    with pytest.raises(ValueError, match=r"confidence must be in \[0, 1\]"):
        IntentTag("develops", evidence="x", confidence=2.0)


def test_intent_tag_serialises_to_the_schema():
    tag = IntentTag("develops", evidence="develops a knight", moves=("g1f3",), confidence=0.9)
    model = tag.to_model()

    assert isinstance(model, IntentTagModel)
    assert model.model_dump() == {
        "tag": "develops",
        "evidence": "develops a knight",
        "moves": ["g1f3"],
        "confidence": 0.9,
    }


# ----------------------------------------------------------------------- static detectors
def test_develops_on_a_developing_move():
    assert "develops" in _tags(chess.Board(), "Nf3")


def test_castles_on_castling():
    b = after("e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5", "d3", "g6")
    assert "castles" in _tags(b, "O-O")


def test_simplifies_on_an_even_exchange():
    b = board("wN@c3", "bN@d5", "bN@f4", "wK@e1", "bK@e8")
    assert "simplifies" in _tags(b, "Nxd5")


def test_attacks_king_on_a_check():
    b = after("e4", "e5", "Bc4", "Nc6", "Qh5", "Nf6")
    assert "attacks_king" in _tags(b, "Qxf7#")


def test_improves_piece_toward_the_centre():
    assert "improves_piece" in _tags(chess.Board(), "Nc3")


def test_restricts_opponent_by_capturing_a_piece():
    b = board("wN@c3", "bN@d5", "wK@e1", "bK@e8")
    assert "restricts_opponent" in _tags(b, "Nxd5")


def test_defends_material_when_a_hanging_piece_is_covered():
    b = board("wQ@d4", "bR@d8", "wP@c2", "wK@e1", "bK@e8")
    assert "defends_material" in _tags(b, "c3")


def test_prepares_break_when_pawns_face_each_other():
    b = board("wP@d4", "bP@e5", "wK@e1", "bK@e8")
    assert "prepares_break" in _tags(b, "d5")


def test_trades_defender_when_a_capture_removes_the_guard():
    b = board("wN@e2", "bR@d4", "bN@b4", "wR@b1", "wK@e1", "bK@e8")
    assert "trades_defender" in _tags(b, "Nxd4")


def test_detect_runs_the_intent_registry():
    b = after("e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5", "d3", "g6")
    tags = detect_intents(
        IntentContext.from_detection(DetectionContext.from_move(b, b.parse_san("O-O")))
    )
    assert {t.tag for t in tags} == {"castles"}


# ---------------------------------------------------------------------------- threat probe
@pytest.mark.engine
def test_threat_probe_runs_without_error(engine_client):
    from moveexp.engine.client import AnalysisLimit

    b = after("e4", "e5", "Nf3", "Nc6", "Bc4", "Nf6")
    move = b.parse_san("Ng5")
    tags = threat_probe(engine_client, b, move, AnalysisLimit.by_depth(8))
    assert isinstance(tags, list)
    assert all(isinstance(tag, IntentTag) for tag in tags)
