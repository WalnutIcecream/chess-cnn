"""Tests for :mod:`moveexp.analysis.see`.

Every expected value is a **hand-computed exchange line**, written next to the case as
``+victim - recaptured ...``, because an SEE implementation that is wrong looks exactly like
one that is right. Fixtures come from :mod:`tests.positions`, which refuses to build an
illegal position, so a case cannot silently stop testing what it claims to test.
"""

from __future__ import annotations

import chess
import pytest

from moveexp.analysis.see import (
    is_sacrifice,
    piece_cp,
    piece_value_cp,
    see_after_move,
    see_capture,
    static_exchange,
)
from positions import after, board


# ------------------------------------------------------------------- piece values
def test_piece_values_come_from_the_config_table():
    assert piece_value_cp(chess.PAWN) == 100
    assert piece_value_cp(chess.KING) == 0
    assert piece_cp(None) == 0
    assert piece_cp(chess.Piece(chess.ROOK, chess.BLACK)) == 500


def test_piece_values_accept_an_override_table():
    assert piece_value_cp(chess.QUEEN, values={"q": 1000}) == 1000
    with pytest.raises(ValueError, match="no configured value"):
        piece_value_cp(chess.QUEEN, values={"p": 100})


# ------------------------------------------------------------------ winning / even
def test_uncontested_capture_wins_the_whole_piece():
    """Rxa8+: +500 rook, nobody can take the rook back."""
    b = board("wR@a1", "bR@a8", "bK@h8", "wK@e1")
    result = see_after_move(b, b.parse_san("Rxa8+"))

    assert result.gain_cp == 500
    assert result.gainer is chess.WHITE
    assert result.target_value_cp == 500
    assert result.attacker_value_cp == 500
    assert result.is_win and not result.is_loss and not result.is_even


def test_even_exchange():
    """Nxd5: +320 knight, then Rx d5 takes it back -> 0."""
    b = board("wN@c3", "bN@d5", "bR@d7", "wK@f1", "bK@f8")
    result = see_after_move(b, b.parse_san("Nxd5"))

    assert result.gain_cp == 0
    assert result.gainer is None
    assert result.is_even


def test_bishop_wins_a_defended_knight_with_a_queen_eye():
    """Bxd5: +100 pawn, then Nf6 takes the bishop (-330), then Qd1 takes the knight (+320)."""
    b = board("wB@c4", "bP@d5", "bN@f6", "wQ@d1", "wK@f1", "bK@f8")
    result = see_after_move(b, b.parse_san("Bxd5"))

    assert result.gain_cp == 100 - 330 + 320 == 90
    assert result.is_win


# --------------------------------------------------------------------- losing line
def test_rook_for_pawn_and_knight_is_a_sacrifice():
    """Rxd5: +100 pawn, Nf6 takes the rook and stops there -> -400."""
    b = board("wR@d1", "bN@f6", "bP@d5", "wK@f1", "bK@f8")
    result = see_after_move(b, b.parse_san("Rxd5"))

    assert result.gain_cp == -400
    assert result.gainer is chess.BLACK
    assert result.is_loss
    assert is_sacrifice(b, b.parse_san("Rxd5")) == (True, -400)


def test_queen_for_rook_plus_pawn():
    """Qxe2: +500 rook, Pd3 takes the queen (-900) -> -400, nothing left to recapture with."""
    b = board("wQ@d1", "bR@e2", "bP@d3", "wK@g1", "bK@g8")
    assert see_after_move(b, b.parse_san("Qxe2")).gain_cp == -400


def test_bishop_for_pawn_and_knight_without_a_follow_up():
    """Bxd5: +100 pawn, Nf6 takes the bishop -> -230."""
    b = board("wB@c4", "bP@d5", "bN@f6", "wK@f1", "bK@f8")
    assert see_after_move(b, b.parse_san("Bxd5")).gain_cp == -230


def test_queen_taking_a_knight_hangs_the_queen():
    """Qxd5: +100 pawn, Nf6 takes the queen (-900) -> -800."""
    b = board("wQ@d1", "bP@d5", "bN@f6", "wK@f1", "bK@f8")
    assert see_after_move(b, b.parse_san("Qxd5")).gain_cp == -800


# ------------------------------------------------------------------------ quiet moves
def test_quiet_move_has_no_exchange_value():
    b = chess.Board()
    result = see_after_move(b, b.parse_san("e4"))

    assert result.gain_cp == 0
    assert result.gainer is None
    assert result.target_value_cp == 0
    assert result.attacker_value_cp == 100
    assert not is_sacrifice(b, b.parse_san("e4"))[0]


def test_king_capture_reports_zero_for_the_attacker():
    b = board("wK@d4", "bP@d5", "bK@f8", "wR@a1")
    result = see_after_move(b, b.parse_san("Kxd5"))

    assert result.gain_cp == 100
    assert result.attacker_value_cp == 0
    assert not is_sacrifice(b, b.parse_san("Kxd5"))[0]


def test_en_passant_wins_the_pawn():
    b = board("wP@e5", "bP@d5", "bK@g8", "wK@g1", "bP@f7", "bR@h8", ep="d6")
    result = see_after_move(b, b.parse_san("exd6"))

    assert result.gain_cp == 100
    assert result.target_value_cp == 100


def test_promotion_capture_is_measured_as_the_capture_only():
    """SEE is material, not promotion: bxa8=Q wins the rook, and the new queen is not counted."""
    b = board("wP@b7", "bR@a8", "bK@f8", "wK@e1")
    assert see_after_move(b, b.parse_san("bxa8=Q")).gain_cp == 500


# ------------------------------------------------------ real moves, real bookkeeping
def test_actual_attacker_is_used_not_the_cheapest_one():
    """Same square, two attackers: the rook wins it, the bishop would only break even.

    ``Rxd5``: +320 knight, Nf6 takes the rook (-500), Bc4 takes the knight back (+320).
    Playing ``Bxd5`` with the same position: +320, then Nf6 (-330), then Rd1 (+320).
    """
    b = board("wR@d1", "wB@c4", "bN@d5", "bN@f6", "wK@f1", "bK@f8")
    square = chess.parse_square("d5")

    assert see_after_move(b, b.parse_san("Rxd5")).gain_cp == 320 - 500 + 320 == 140
    assert static_exchange(b, square, chess.WHITE) == 320 - 330 + 320 == 310


def test_scholars_mate_queen_take_is_mate_but_only_a_pawn_on_see():
    """``Qxf7#`` is defended only by the king, so the exchange is simply a won pawn.

    SEE says nothing about mate: that is the engine's job, and this is why the M2 detectors
    never trust SEE on its own.
    """
    b = after("e4", "e5", "Bc4", "Nc6", "Qh5", "Nf6")
    result = see_after_move(b, b.parse_san("Qxf7#"))

    assert result.gain_cp == 100
    assert result.is_win


def test_king_recapture_is_excluded_by_design():
    """Rh7+ gains 500 according to SEE, but the king simply takes the rook back.

    Kings are never part of an exchange sequence, so SEE cannot see this. The engine check in
    ``classify_special`` is what catches such moves -- which is why every sacrifice theme
    requires engine confirmation before it is reported.
    """
    b = board("wR@h1", "bR@h7", "bK@h8", "wK@e1")
    assert see_after_move(b, b.parse_san("Rh7+")).gain_cp == 500


# ------------------------------------------------------------------ static_exchange
def test_static_exchange_needs_a_hostile_piece():
    b = board("wN@c3", "bN@d5", "bR@d7", "wK@f1", "bK@f8")
    own_knight = chess.parse_square("c3")
    empty = chess.parse_square("a4")

    assert static_exchange(b, own_knight, chess.WHITE) == 0
    assert static_exchange(b, empty, chess.WHITE) == 0


def test_static_exchange_answers_from_the_owning_side_only():
    # The white king is on h1 rather than f1 on purpose: a king on f1 would be attacked by the
    # black bishop, which makes the position legal but every capture illegal.
    white_owned = board("wR@d1", "wN@d5", "bB@c4", "wK@h1", "bK@f8")
    black_owned = board("wR@d1", "bN@d5", "bB@c4", "wK@h1", "bK@f8")
    d5 = chess.parse_square("d5")

    # White owns the knight: Bc4 takes it (+320), then Rd1 takes the bishop (-330) -> -10.
    assert static_exchange(white_owned, d5, chess.BLACK) == -10
    # Black owns it: Rd1 takes it (+320), then Bc4 takes the rook (-500) -> -180.
    assert static_exchange(black_owned, d5, chess.WHITE) == -180
    # A square holding the querying side's own piece is not an exchange at all.
    assert static_exchange(white_owned, d5, chess.WHITE) == 0


def test_static_exchange_respects_a_custom_value_table():
    b = board("wR@a1", "bR@a8", "bK@h8", "wK@e1")
    assert static_exchange(b, chess.parse_square("a8"), chess.WHITE, values={"r": 700}) == 700


# -------------------------------------------------------------------- is_sacrifice
def test_knight_for_a_pawn_is_a_sacrifice_but_a_pawn_capture_is_not():
    b = board("wN@d3", "bP@e5", "bN@c6", "wK@g1", "bK@g8")
    assert is_sacrifice(b, b.parse_san("Nxe5")) == (True, -220)

    free = board("wN@d3", "bP@e5", "wK@g1", "bK@g8")
    assert is_sacrifice(free, free.parse_san("Nxe5")) == (False, 100)


def test_pawn_capture_is_never_a_sacrifice_but_still_reports_its_gain():
    """A pawn is the cheapest capturer there is, so its exchanges can never look like a loss.

    ``exd5``: +320 knight, Nf6 takes the pawn (-100) -> +220. The gain is reported even though
    the pawn is too cheap for the sacrifice test to care about it.
    """
    b = board("wP@e4", "bN@d5", "bN@f6", "wK@h1", "bK@f8")
    assert is_sacrifice(b, b.parse_san("exd5")) == (False, 220)


def test_king_move_is_never_a_sacrifice():
    b = board("wK@d4", "bP@d5", "bK@f8", "wR@a1")
    # A king is not part of any exchange, but the pawn it takes is still a real gain.
    assert is_sacrifice(b, b.parse_san("Kxd5")) == (False, 100)


def test_custom_sacrifice_thresholds():
    b = board("wN@d3", "bP@e5", "bN@c6", "wK@g1", "bK@g8")
    move = b.parse_san("Nxe5")

    assert is_sacrifice(b, move, margin_cp=1000) == (False, -220)
    assert is_sacrifice(b, move, min_piece_cp=1000) == (False, -220)


# ------------------------------------------------------------------------- validation
def test_see_capture_rejects_quiet_moves():
    b = board("wR@d1", "bP@e5", "wK@g1", "bK@g8")

    with pytest.raises(ValueError, match="not a capture"):
        see_capture(b, b.parse_san("Rd3"))


def test_illegal_moves_are_rejected():
    # d1xe5 is capture-shaped (a black pawn stands there) but no rook can reach e5 that way, so
    # the only thing wrong with it is legality.
    b = board("wR@d1", "bP@e5", "wK@g1", "bK@g8")
    impossible = chess.Move.from_uci("d1e5")

    with pytest.raises(ValueError, match="not legal"):
        see_capture(b, impossible)
    with pytest.raises(ValueError, match="not legal"):
        see_after_move(b, impossible)
