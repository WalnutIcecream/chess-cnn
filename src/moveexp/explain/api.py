"""High-level entry points: analyse a move or a game and explain it.

These wrap :mod:`moveexp.pipeline`, so the explanation always sits on top of a fully
populated :class:`~moveexp.schema.MoveReport`.
"""

from __future__ import annotations

from dataclasses import dataclass

import chess
import chess.pgn

from ..pipeline import analyse_game, analyse_move
from ..schema import GameReport, MoveReport
from .models import Explanation
from .render import render_explanation


@dataclass
class MoveExplanation:
    """A move report together with its verified explanation."""

    report: MoveReport
    explanation: Explanation


@dataclass
class GameExplanation:
    """A game report together with the explanation of every move."""

    game: GameReport
    explanations: list[Explanation]


def explain_move(board: chess.Board, move: chess.Move, **kwargs) -> MoveExplanation:
    """Analyse ``move`` in ``board`` and return the report plus its explanation.

    Accepts the same keyword arguments as :func:`moveexp.pipeline.analyse_move`.
    """
    report = analyse_move(board, move, **kwargs)
    return MoveExplanation(report=report, explanation=render_explanation(report))


def explain_game(game: chess.pgn.Game, **kwargs) -> GameExplanation:
    """Analyse every move of ``game`` and explain each one."""
    report = analyse_game(game, **kwargs)
    explanations = [render_explanation(move) for move in report.moves]
    return GameExplanation(game=report, explanations=explanations)


def format_move_explanation(explanation: MoveExplanation) -> str:
    """Plain-text rendering of a single move's explanation."""
    return explanation.explanation.text()


def format_game_explanation(explanation: GameExplanation) -> str:
    """Markdown rendering of a whole game: one section per move."""
    players = explanation.game.players
    lines = [
        f"# {explanation.game.game_id}",
        f"{players.get('white', '?')} vs {players.get('black', '?')} — "
        f"{explanation.game.result or '*'}",
        "",
    ]
    for move in explanation.explanations:
        number = move.ply // 2 + 1
        label = f"{number}." if move.ply % 2 == 0 else f"{number}..."
        lines.append(f"## {label} {move.headline}")
        lines.extend(f"- {sentence}" for sentence in move.sentences)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
