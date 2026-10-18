"""Neural baseline: encode a position+moves as tensors and predict the rule labels.

Importing this package is torch-free (only :mod:`encode` and :mod:`dataset` are pulled
in); the network is imported explicitly from :mod:`moveexp.model.network` so the symbolic
stack keeps working without the optional ``torch`` extra installed.
"""

from .dataset import build_dataset, build_intent_targets, build_puzzle_dataset, group_split
from .encode import (
    N_PLANES,
    augment_planes,
    colour_flip,
    encode_board,
    mirror_files,
    n_planes,
)

__all__ = [
    "N_PLANES",
    "augment_planes",
    "build_dataset",
    "build_intent_targets",
    "build_puzzle_dataset",
    "colour_flip",
    "encode_board",
    "group_split",
    "mirror_files",
    "n_planes",
]
