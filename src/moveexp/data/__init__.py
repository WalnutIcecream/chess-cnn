"""Data acquisition: download public corpora and stream them without unpacking.

Nothing in this package is imported by the analysis or explanation layers -- it is the
only part of ``moveexp`` that knows about the network, and it is deliberately kept out of
``src/moveexp``'s other imports so the symbolic stack stays offline.

Currently the Lichess open database (CC0) is the only source:

* :mod:`moveexp.data.lichess` -- resumable download plus streaming ``.zst`` readers,
* :mod:`moveexp.data.puzzle_themes` -- the Lichess puzzle tag vocabulary and its mapping
  onto :data:`moveexp.config.THEME_VOCAB`.
"""

from .lichess import (
    PUZZLE_URL,
    Puzzle,
    download,
    iter_lines,
    open_text,
    stream_games,
    stream_puzzles,
)

__all__ = [
    "PUZZLE_URL",
    "Puzzle",
    "download",
    "iter_lines",
    "open_text",
    "stream_games",
    "stream_puzzles",
]
