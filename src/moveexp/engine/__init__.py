"""Engine layer: process lifecycle, result cache and score conversion.

The perspective rule for the whole project lives in :mod:`moveexp.engine.eval_utils`.
"""

from __future__ import annotations

from .cache import AnalysisCache, CacheStats, make_cache_key
from .client import (
    AnalysisLimit,
    ClientStats,
    EngineCrashedError,
    EngineError,
    EngineNotRunningError,
    StockfishClient,
)

__all__ = [
    "AnalysisCache",
    "AnalysisLimit",
    "CacheStats",
    "ClientStats",
    "EngineCrashedError",
    "EngineError",
    "EngineNotRunningError",
    "StockfishClient",
    "make_cache_key",
]
