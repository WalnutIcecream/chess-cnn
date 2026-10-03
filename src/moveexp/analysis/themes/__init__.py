"""Stage 2 theme detectors: the symbolic explanations attached to a played move.

* :mod:`moveexp.analysis.themes.base` -- the hit record, the shared context, the registry.
* :mod:`moveexp.analysis.themes.common` -- shared attack/defence counting and piece values.
* Detector modules register themselves when imported. Call :func:`register_all` to populate the
  registry with all built-in detectors, or import individual detector modules explicitly.

Detector modules are ordinary pure functions. To have the full set registered::

    from moveexp.analysis.themes import detect, register_all

    register_all()
    hits = detect(board, move)
"""

from .base import (
    REGISTRY,
    DetectionContext,
    Detector,
    DetectorReport,
    HitResult,
    ThemeHit,
    detect,
    detector,
    iter_themes,
    piece_label,
    registered_detectors,
    run_all,
    theme_order,
    validate_theme,
)


def register_all() -> None:
    """Import every built-in detector module so that it registers itself."""
    from . import activity as _activity  # noqa: F401
    from . import king_safety as _king_safety  # noqa: F401
    from . import material as _material  # noqa: F401
    from . import structure as _structure  # noqa: F401
    from . import tactics as _tactics  # noqa: F401

    # Importing is sufficient because each module calls ``@detector`` at import time.


__all__ = [
    "REGISTRY",
    "DetectionContext",
    "Detector",
    "DetectorReport",
    "HitResult",
    "ThemeHit",
    "detect",
    "detector",
    "iter_themes",
    "piece_label",
    "register_all",
    "registered_detectors",
    "run_all",
    "theme_order",
    "validate_theme",
]
