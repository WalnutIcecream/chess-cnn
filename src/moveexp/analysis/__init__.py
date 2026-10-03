"""Stage 1: turn engine lines into a move-quality label and criticality signals.

* :mod:`moveexp.analysis.move_quality` -- eval deltas, win-probability loss, labels.
* :mod:`moveexp.analysis.criticality` -- only-move / sharpness / forcing / critical.
* :mod:`moveexp.analysis.see` -- static exchange value, the material half of every M2 theme.

Both modules take raw engine lines (scores relative to the analysed position's side to
move) and return values in the **mover's** point of view.
"""

from __future__ import annotations

from .criticality import Criticality, assess_criticality, gap_to_second_wp, is_forcing, sharpness
from .move_quality import MoveQuality, assess_move, classify_loss, classify_special
from .see import SeeResult, is_sacrifice, piece_cp, piece_value_cp, see_after_move, see_capture

__all__ = [
    "Criticality",
    "MoveQuality",
    "SeeResult",
    "assess_criticality",
    "assess_move",
    "classify_loss",
    "classify_special",
    "gap_to_second_wp",
    "is_forcing",
    "is_sacrifice",
    "piece_cp",
    "piece_value_cp",
    "see_after_move",
    "see_capture",
    "sharpness",
]
