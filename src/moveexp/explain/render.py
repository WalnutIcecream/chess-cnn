"""Assemble a :class:`~moveexp.explain.models.Explanation` from a move report.

The renderer is intentionally thin: it turns each :class:`~moveexp.explain.facts.Fact`
into a claim in the order the facts were built, then hands the whole set to the verifier.
Text ordering, not wording, is the only thing this module decides.
"""

from __future__ import annotations

from ..schema import MoveReport
from .facts import facts_from_report
from .models import ClaimModel, Explanation
from .verify import verify_claims


def render_explanation(report: MoveReport) -> Explanation:
    """Build and verify the explanation for one move report."""
    facts = facts_from_report(report)
    claims = [
        ClaimModel(
            kind=fact.kind,
            text=fact.text,
            evidence=fact.evidence,
            source=dict(fact.source),
        )
        for fact in facts
    ]
    claims, unverified = verify_claims(claims, report)

    headline = next((c.text for c in claims if c.kind == "headline"), report.move_san)
    sentences = [c.text for c in claims if c.kind != "headline"]
    return Explanation(
        ply=report.ply,
        move_san=report.move_san,
        move_uci=report.move_uci,
        headline=headline,
        sentences=sentences,
        claims=claims,
        unverified=unverified,
        verified=not unverified,
    )
