"""Independently re-derive every claim from the report it came from.

Verification is deliberately a second pass over the :class:`~moveexp.schema.MoveReport`,
not a re-run of the renderer: it reads the claim's ``source`` values and checks them
against the report's fields. A claim whose fact no longer holds is marked unverified and
never reaches the reader, which is what makes the explanation *constrained* rather than
merely templated.
"""

from __future__ import annotations

from ..schema import MoveReport
from .models import ClaimModel

#: Tolerance for float comparisons (the values are copied, not recomputed, so this only
#: guards against a stale report being handed to a verifier).
_TOL = 1e-6


def _check(claim: ClaimModel, report: MoveReport) -> tuple[bool, str]:
    """Return ``(ok, reason)`` for one claim."""
    kind = claim.kind
    source = claim.source
    quality = report.quality

    if kind == "headline":
        if source.get("label") != quality.label:
            return False, f"label {source.get('label')!r} != report {quality.label!r}"
        return True, ""

    if kind == "evaluation":
        if source.get("label") != quality.label:
            return False, "quality label changed"
        if abs(float(source.get("loss_cp", 0.0)) - quality.loss_cp) > _TOL:
            return False, "loss_cp changed"
        return True, ""

    if kind == "criticality":
        flag = source.get("flag")
        if not isinstance(flag, str) or not hasattr(quality, flag):
            return False, f"unknown flag {flag!r}"
        if bool(getattr(quality, flag)) != bool(source.get("value")):
            return False, f"{flag} is no longer true"
        return True, ""

    if kind == "theme":
        if source.get("theme") not in report.theme_names:
            return False, f"theme {source.get('theme')!r} not in report"
        return True, ""

    if kind == "positional":
        group = source.get("group")
        delta = report.positional_delta.model_dump()
        if group not in delta:
            return False, f"unknown positional group {group!r}"
        if abs(float(delta[group] or 0.0) - float(source.get("value", 0.0))) > _TOL:
            return False, f"{group} value changed"
        return True, ""

    if kind == "intent":
        if source.get("tag") not in report.intent_tags:
            return False, f"intent {source.get('tag')!r} not in report"
        return True, ""

    if kind == "engine":
        if source.get("best_move") != quality.best_move:
            return False, "best_move changed"
        return True, ""

    return False, f"no verifier for claim kind {kind!r}"


def verify_claims(
    claims: list[ClaimModel], report: MoveReport
) -> tuple[list[ClaimModel], list[str]]:
    """Split ``claims`` into those the report supports and a list of failure reasons."""
    verified: list[ClaimModel] = []
    unverified: list[str] = []
    for claim in claims:
        ok, reason = _check(claim, report)
        claim = claim.model_copy(update={"verified": ok})
        if ok:
            verified.append(claim)
        else:
            unverified.append(f"{claim.kind}: {reason}")
    return verified, unverified
