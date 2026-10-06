"""Verified natural-language explanations built strictly from a ``MoveReport``.

The layer has four small parts: :mod:`facts` derives checkable clauses from a report,
:mod:`render` orders them into prose, :mod:`verify` re-derives every claim from the same
report, and :mod:`api` wires it onto the analysis pipeline. Nothing here invents a fact
that is not already in the report.
"""

from .api import (
    GameExplanation,
    MoveExplanation,
    explain_game,
    explain_move,
    format_game_explanation,
    format_move_explanation,
)
from .facts import Fact, facts_from_report
from .models import ClaimModel, Explanation
from .render import render_explanation
from .verify import verify_claims

__all__ = [
    "ClaimModel",
    "Explanation",
    "Fact",
    "GameExplanation",
    "MoveExplanation",
    "explain_game",
    "explain_move",
    "facts_from_report",
    "format_game_explanation",
    "format_move_explanation",
    "render_explanation",
    "verify_claims",
]
