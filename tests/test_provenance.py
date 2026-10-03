"""Engine provenance: recorded per report and flattened for Parquet round-trips."""

from __future__ import annotations

from moveexp.schema import EngineProvenance, MoveReport, QualityInfo

FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def _report() -> MoveReport:
    return MoveReport(
        ply=1,
        fen_before=FEN,
        move_uci="e2e4",
        move_san="e4",
        quality=QualityInfo(
            label="best",
            eval_before_cp=0.0,
            eval_after_cp=20.0,
            win_prob_before=0.5,
            win_prob_after=0.52,
        ),
        provenance=EngineProvenance(
            engine_name="Stockfish 19",
            engine_author="T. Romstad et al.",
            limit_type="depth",
            limit_value=16,
            multipv=3,
            threads=1,
            hash_mb=256,
            moveexp_version="0.1.0",
        ),
    )


def test_provenance_defaults_are_empty():
    empty = EngineProvenance()
    assert empty.engine_name == "" and empty.limit_type == "" and empty.limit_value is None


def test_provenance_is_flattened_and_round_trips():
    row = _report().to_flat_row()
    assert row["prov_engine_name"] == "Stockfish 19"
    assert row["prov_engine_author"] == "T. Romstad et al."
    assert row["prov_limit_type"] == "depth"
    assert row["prov_limit_value"] == 16
    assert row["prov_multipv"] == 3

    restored = MoveReport.from_flat_row(row)
    assert restored.provenance == _report().provenance
