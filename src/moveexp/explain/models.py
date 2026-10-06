"""Serialisable models for the explanation layer.

An :class:`Explanation` is prose plus, for every sentence, a :class:`ClaimModel` that
names the report field it came from. That pairing is the whole point of the layer: the
text can never say something the :class:`~moveexp.schema.MoveReport` does not contain,
because each sentence is verified against the report before it is emitted.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ClaimModel(BaseModel):
    """One sentence of an explanation, tied to the fact that justifies it."""

    model_config = ConfigDict(validate_assignment=True)

    kind: str
    """``headline`` | ``evaluation`` | ``criticality`` | ``theme`` | ``positional`` |
    ``intent`` | ``engine``."""

    text: str
    """The sentence as rendered."""

    evidence: str = ""
    """Human-readable back-reference to the report fields used (for the audit trail)."""

    source: dict[str, Any] = Field(default_factory=dict)
    """The raw values the claim was built from, so a verifier can re-derive it."""

    confidence: float = 1.0
    """Inherited from the detector (1.0 for exact rule matches)."""

    verified: bool = True
    """Whether :func:`moveexp.explain.verify.verify_claims` could re-derive this claim."""


class Explanation(BaseModel):
    """A verified natural-language explanation of one move."""

    model_config = ConfigDict(validate_assignment=True)

    ply: int
    move_san: str
    move_uci: str
    headline: str
    """The one-line summary, e.g. ``"Qxf7# — a brilliant move."``"""

    sentences: list[str] = Field(default_factory=list)
    """The body sentences, in presentation order (headline excluded)."""

    claims: list[ClaimModel] = Field(default_factory=list)
    """Every emitted claim, headline included, in presentation order."""

    unverified: list[str] = Field(default_factory=list)
    """Claims that failed verification (dropped from ``sentences``). Empty is the goal."""

    verified: bool = True
    """True when every claim passed verification."""

    def text(self) -> str:
        """The explanation as indented plain text."""
        body = [f"  {s}" for s in self.sentences]
        return "\n".join([self.headline, *body])
