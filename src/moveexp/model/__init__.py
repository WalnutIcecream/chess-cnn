"""Neural baseline: encode a position+moves as tensors and predict the rule labels.

Importing this package is torch-free (only :mod:`encode` and :mod:`dataset` are pulled
in); the network is imported explicitly from :mod:`moveexp.model.network` so the symbolic
stack keeps working without the optional ``torch`` extra installed.
"""

from .dataset import build_dataset, build_intent_targets, group_split
from .encode import N_PLANES, encode_board, n_planes

__all__ = [
    "N_PLANES",
    "build_dataset",
    "build_intent_targets",
    "encode_board",
    "group_split",
    "n_planes",
]
