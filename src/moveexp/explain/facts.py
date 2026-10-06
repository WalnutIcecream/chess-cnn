"""Derive the atomic, checkable facts of a :class:`~moveexp.schema.MoveReport`.

A :class:`Fact` is a single sentence-ready clause plus the report values it was built
from. Facts are ordered the way an explanation should read: verdict first, then
criticality, tactics, positional change, intent, and finally the engine's dissent.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..schema import IntentTagModel, MoveReport, ThemeHitModel

#: A positional group is only worth mentioning past these magnitudes. ``material`` is in
#: centi-pawns; the rest are feature units on the (coarse) ``FEATURE_WEIGHTS`` scale.
POSITIONAL_THRESHOLD: dict[str, float] = {
    "material": 50.0,
    "mobility": 4.0,
    "king_safety": 4.0,
    "pawn_structure": 10.0,
    "space": 2.0,
    "activity": 3.0,
}

#: Fixed presentation order for the positional groups.
POSITIONAL_ORDER: tuple[str, ...] = (
    "material",
    "mobility",
    "king_safety",
    "pawn_structure",
    "space",
    "activity",
)

#: Labels that mean "this move did not give anything away".
POSITIVE_QUALITY: tuple[str, ...] = ("best", "great", "brilliant", "excellent")

_QUALITY_PHRASE: dict[str, str] = {
    "best": "the best move",
    "great": "a great move",
    "brilliant": "a brilliant move",
    "excellent": "an excellent move",
    "good": "a good move",
    "inaccuracy": "an inaccuracy",
    "mistake": "a mistake",
    "blunder": "a blunder",
}


@dataclass(frozen=True)
class Fact:
    """One verifiable clause and the report values behind it."""

    id: str
    kind: str
    text: str
    evidence: str
    source: dict[str, Any]


def quality_phrase(label: str) -> str:
    """Human noun phrase for a quality label (``'a mistake'``, ``'the best move'``)."""
    return _QUALITY_PHRASE.get(label, f"a {label} move")


def _describe_eval(cp: float) -> str:
    """Render a centi-pawn evaluation that may be a folded mate score."""
    if cp >= 9000.0:
        return "winning by force"
    if cp <= -9000.0:
        return "losing by force"
    return f"{cp / 100:+.2f} for the mover"


def _headline_fact(report: MoveReport) -> Fact:
    san = report.move_san or report.move_uci
    return Fact(
        id="headline",
        kind="headline",
        text=f"{san} — {quality_phrase(report.quality.label)}.",
        evidence=f"quality.label={report.quality.label}",
        source={"move_san": san, "label": report.quality.label},
    )


def _evaluation_fact(report: MoveReport) -> Fact:
    q = report.quality
    if q.label in POSITIVE_QUALITY:
        text = f"The evaluation remains {_describe_eval(q.eval_after_cp)}."
    else:
        text = f"It gives up {q.loss_cp / 100:.2f} pawns ({q.loss_wp * 100:.0f}% win probability)."
    return Fact(
        id="evaluation",
        kind="evaluation",
        text=text,
        evidence=(
            f"eval_before_cp={q.eval_before_cp:.1f}, eval_after_cp={q.eval_after_cp:.1f}, "
            f"loss_cp={q.loss_cp:.1f}, loss_wp={q.loss_wp:.3f}"
        ),
        source={
            "label": q.label,
            "eval_after_cp": q.eval_after_cp,
            "loss_cp": q.loss_cp,
            "loss_wp": q.loss_wp,
        },
    )


def _criticality_facts(report: MoveReport) -> list[Fact]:
    q = report.quality
    facts: list[Fact] = []
    if q.is_only_move:
        facts.append(
            Fact(
                id="criticality:only_move",
                kind="criticality",
                text="It was the only move that keeps the position.",
                evidence=f"is_only_move=True, gap_to_second_wp={q.gap_to_second_wp:.3f}",
                source={"flag": "is_only_move", "value": True},
            )
        )
    if q.is_forcing:
        facts.append(
            Fact(
                id="criticality:forcing",
                kind="criticality",
                text="The move is forcing: a check or a forced mate.",
                evidence="is_forcing=True",
                source={"flag": "is_forcing", "value": True},
            )
        )
    if q.is_critical:
        facts.append(
            Fact(
                id="criticality:critical",
                kind="criticality",
                text="The position was critical: small differences in the evaluation mattered.",
                evidence=f"is_critical=True, sharpness={q.sharpness:.3f}",
                source={"flag": "is_critical", "value": True},
            )
        )
    return facts


def _theme_fact(hit: ThemeHitModel) -> Fact:
    label = hit.theme.replace("_", " ")
    evidence = hit.evidence.rstrip(".")
    text = f"{label.capitalize()}: {evidence}." if evidence else f"{label.capitalize()}."
    return Fact(
        id=f"theme:{hit.theme}",
        kind="theme",
        text=text,
        evidence=hit.evidence,
        source={
            "theme": hit.theme,
            "squares": list(hit.squares),
            "pieces": list(hit.pieces),
            "confidence": hit.confidence,
        },
    )


def _move_decides_the_game(report: MoveReport) -> bool:
    """Whether the move forces a win, making positional feature deltas meaningless.

    On a mating move the "position after" is effectively terminal, so mobility, space
    and the rest are artifacts of the final board rather than a signal about intent.
    """
    return report.quality.eval_after_cp >= 9000.0


def _positional_facts(report: MoveReport) -> list[Fact]:
    if _move_decides_the_game(report):
        return []
    delta = report.positional_delta.model_dump()
    facts: list[Fact] = []
    for group in POSITIONAL_ORDER:
        value = float(delta.get(group, 0.0) or 0.0)
        if abs(value) < POSITIONAL_THRESHOLD.get(group, 1.0):
            continue
        if group == "material":
            direction = "gained" if value > 0 else "lost"
            text = f"Material: the mover {direction} {abs(value) / 100:.2f} pawns."
        else:
            direction = "improved" if value > 0 else "worsened"
            text = f"{group.replace('_', ' ').capitalize()}: {direction} by {abs(value):.1f}."
        facts.append(
            Fact(
                id=f"positional:{group}",
                kind="positional",
                text=text,
                evidence=f"positional_delta.{group}={value:.1f}",
                source={"group": group, "value": value},
            )
        )
    return facts


def _intent_fact(tag: IntentTagModel) -> Fact:
    label = tag.tag.replace("_", " ")
    evidence = tag.evidence.rstrip(".")
    text = f"Intent — {label}: {evidence}." if evidence else f"Intent — {label}."
    return Fact(
        id=f"intent:{tag.tag}",
        kind="intent",
        text=text,
        evidence=tag.evidence,
        source={"tag": tag.tag, "moves": list(tag.moves), "confidence": tag.confidence},
    )


def _engine_fact(report: MoveReport) -> Fact | None:
    q = report.quality
    if q.label in POSITIVE_QUALITY or not q.best_move:
        return None
    name = q.best_move_san or q.best_move
    return Fact(
        id="engine:best_move",
        kind="engine",
        text=f"The engine preferred {name}.",
        evidence=f"best_move={q.best_move}, label={q.label}",
        source={"best_move": q.best_move, "label": q.label},
    )


def facts_from_report(report: MoveReport) -> list[Fact]:
    """Build the ordered fact list for one move.

    Themes and intents are de-duplicated (first occurrence wins) and kept in detection
    order, because the detectors deliberately surface the most important theme first.
    """
    facts: list[Fact] = [_headline_fact(report), _evaluation_fact(report)]
    facts.extend(_criticality_facts(report))

    seen_themes: set[str] = set()
    for hit in report.themes:
        if hit.theme in seen_themes:
            continue
        seen_themes.add(hit.theme)
        facts.append(_theme_fact(hit))

    facts.extend(_positional_facts(report))

    seen_intents: set[str] = set()
    for tag in report.intent:
        if tag.tag in seen_intents:
            continue
        seen_intents.add(tag.tag)
        facts.append(_intent_fact(tag))

    engine_fact = _engine_fact(report)
    if engine_fact is not None:
        facts.append(engine_fact)
    return facts
