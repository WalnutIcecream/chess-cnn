"""moveexp -- explain the intent, tactical importance and positional effect of a move.

Layer 1 (symbolic, Stages 1-2): Stockfish evaluation + python-chess rules produce a
:class:`~moveexp.schema.MoveReport`.
Layer 2 (dataset, Stage 3): the symbolic layer runs at scale over sampled positions.
Layer 3 (learning, Stages 4-5): a network learns the labels, an LLM writes the prose.

Importing this package is cheap: it does not start an engine, touch the filesystem or
import pandas / torch. Import the submodules you need explicitly.
"""

from __future__ import annotations

__version__ = "0.1.0"

__all__ = ["__version__"]
