"""Vocabulary/detector coverage: the registered detectors must cover the vocab exactly.

A theme (or intent) in the frozen vocabulary with no detector would produce an all-zero
label column, which breaks class-weighted losses; a detector emitting a name *not* in the
vocabulary would be dropped silently by :func:`moveexp.schema.theme_multi_hot`. These tests
pin both directions so the two can never drift apart.
"""

from __future__ import annotations

from moveexp.analysis.themes import register_all
from moveexp.analysis.themes.base import registered_detectors
from moveexp.analysis.themes.intent import ENGINE_INTENT_TAGS, registered_intents
from moveexp.config import INTENT_VOCAB, THEME_VOCAB

register_all()


def test_theme_detectors_cover_theme_vocab_exactly():
    names = {func.__name__[len("detect_") :] for func in registered_detectors()}
    assert names == set(THEME_VOCAB)


def test_intent_detectors_cover_intent_vocab_exactly():
    # Static detectors are named ``_<tag>``; the engine-backed tags are the remainder.
    static = {func.__name__.lstrip("_") for func in registered_intents()}
    assert static | set(ENGINE_INTENT_TAGS) == set(INTENT_VOCAB)
