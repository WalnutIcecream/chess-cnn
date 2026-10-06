"""Tests for the explanation layer (facts -> render -> verify).

No engine is needed: a :class:`MoveReport` is built directly and the explainer is checked
against it, including the failure path where a claim the report does not support must be
dropped rather than printed.
"""

from __future__ import annotations

from moveexp.explain import (
    GameExplanation,
    facts_from_report,
    format_game_explanation,
    render_explanation,
    verify_claims,
)
from moveexp.explain.models import ClaimModel, Explanation
from moveexp.schema import (
    GameReport,
    IntentTagModel,
    MoveReport,
    PositionalDelta,
    QualityInfo,
    ThemeHitModel,
)

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def make_report(
    *,
    label: str = "great",
    themes: list[ThemeHitModel] | None = None,
    positional_delta: PositionalDelta | None = None,
    intent: list[IntentTagModel] | None = None,
    best_move: str | None = "f3f7",
    eval_after_cp: float = 100.0,
    **quality_overrides: object,
) -> MoveReport:
    quality = QualityInfo(
        label=label,
        eval_before_cp=100.0,
        eval_after_cp=eval_after_cp,
        win_prob_before=0.6,
        win_prob_after=0.6,
        loss_cp=0.0,
        loss_wp=0.0,
        best_move=best_move,
        best_move_san="Qxf7#",
        is_only_move=bool(quality_overrides.pop("is_only_move", True)),
        is_forcing=bool(quality_overrides.pop("is_forcing", True)),
        is_critical=bool(quality_overrides.pop("is_critical", False)),
    )
    return MoveReport(
        ply=6,
        fen_before=START_FEN,
        fen_after=START_FEN,
        move_uci="f3f7",
        move_san="Qxf7#",
        quality=quality,
        themes=themes
        if themes is not None
        else [
            ThemeHitModel(
                theme="fork",
                squares=["f7", "e8"],
                pieces=["Q@f7"],
                confidence=1.0,
                evidence="Q@f7 hits b@f8 and n@g8 at once and does not hang",
            )
        ],
        positional_delta=positional_delta if positional_delta is not None else PositionalDelta(),
        intent=intent if intent is not None else [],
    )


def test_headline_and_all_claims_verify() -> None:
    explanation = render_explanation(make_report())
    assert explanation.verified is True
    assert explanation.unverified == []
    assert explanation.headline == "Qxf7# — a great move."
    assert all(claim.verified for claim in explanation.claims)


def test_theme_claim_is_present_and_evidence_backed() -> None:
    explanation = render_explanation(make_report())
    theme_claims = [c for c in explanation.claims if c.kind == "theme"]
    assert len(theme_claims) == 1
    assert theme_claims[0].source["theme"] == "fork"
    assert theme_claims[0].text.startswith("Fork:")
    assert theme_claims[0].evidence


def test_criticality_claims_follow_the_flags() -> None:
    only = render_explanation(make_report(is_only_move=True, is_forcing=False))
    assert any(c.kind == "criticality" for c in only.claims)

    quiet = render_explanation(make_report(is_only_move=False, is_forcing=False, is_critical=False))
    assert not any(c.kind == "criticality" for c in quiet.claims)


def test_positional_claim_respects_threshold() -> None:
    big = render_explanation(make_report(positional_delta=PositionalDelta(material=500.0)))
    assert any(c.source.get("group") == "material" for c in big.claims)

    small = render_explanation(make_report(positional_delta=PositionalDelta(material=10.0)))
    assert not any(c.source.get("group") == "material" for c in small.claims)


def test_positional_claims_suppressed_on_a_decided_move() -> None:
    report = make_report(positional_delta=PositionalDelta(material=500.0), eval_after_cp=9999.0)
    explanation = render_explanation(report)
    assert not any(c.kind == "positional" for c in explanation.claims)


def test_intent_claim_is_rendered() -> None:
    report = make_report(intent=[IntentTagModel(tag="attacks_king", evidence="Qxf7# gives check")])
    explanation = render_explanation(report)
    intent_claims = [c for c in explanation.claims if c.kind == "intent"]
    assert intent_claims[0].text == "Intent — attacks king: Qxf7# gives check."
    assert explanation.verified


def test_engine_claim_only_when_move_was_not_best() -> None:
    good = render_explanation(make_report(label="great"))
    assert not any(c.kind == "engine" for c in good.claims)

    bad = render_explanation(
        make_report(label="mistake", best_move="d1h5", is_only_move=False, is_forcing=False)
    )
    engine_claims = [c for c in bad.claims if c.kind == "engine"]
    assert engine_claims and engine_claims[0].source["best_move"] == "d1h5"


def test_mate_evaluation_is_described_not_printed_as_number() -> None:
    explanation = render_explanation(make_report(eval_after_cp=9999.0))
    evaluation = next(c for c in explanation.claims if c.kind == "evaluation")
    assert "winning by force" in evaluation.text


def test_unsupported_claim_is_dropped_by_verification() -> None:
    report = make_report()
    bogus = ClaimModel(
        kind="theme",
        text="Deflection: the queen lures a defender away.",
        source={"theme": "deflection"},
    )
    verified, unverified = verify_claims([bogus], report)
    assert verified == []
    assert unverified and "deflection" in unverified[0]


def test_facts_are_deduplicated_by_theme() -> None:
    dup = ThemeHitModel(theme="fork", evidence="first")
    dup2 = ThemeHitModel(theme="fork", evidence="second")
    report = make_report(themes=[dup, dup2])
    theme_ids = [f.id for f in facts_from_report(report) if f.kind == "theme"]
    assert theme_ids == ["theme:fork"]


def test_text_rendering_indents_body() -> None:
    explanation = render_explanation(make_report())
    text = explanation.text()
    assert text.splitlines()[0] == explanation.headline
    assert all(line.startswith("  ") for line in text.splitlines()[1:])


def test_format_game_explanation_numbers_moves_from_ply() -> None:
    game = GameReport(game_id="g", players={"white": "A", "black": "B"}, result="1-0")
    first = Explanation(
        ply=6,
        move_san="Qxf7#",
        move_uci="f3f7",
        headline="Qxf7# — a great move.",
        sentences=["It was the only move that keeps the position."],
    )
    second = Explanation(ply=7, move_san="Kxf7", move_uci="e8f7", headline="Kxf7 — a blunder.")
    markdown = format_game_explanation(GameExplanation(game=game, explanations=[first, second]))
    assert "A vs B — 1-0" in markdown
    assert "## 4. Qxf7# — a great move." in markdown
    assert "## 4... Kxf7 — a blunder." in markdown
    assert "- It was the only move that keeps the position." in markdown
