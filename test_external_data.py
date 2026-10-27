"""Resmi açık veri adaptörleri ve provenance sözleşmesi testleri."""
from pathlib import Path

import pandas as pd
import pytest

from src.rcz_topsis.external_data import (
    SOURCE_SPECS,
    build_provenance,
    to_decision_matrix,
)


def test_both_validation_lines_have_official_sources():
    assert SOURCE_SPECS["ted_open_data"].publisher
    assert SOURCE_SPECS["nasa_phm"].publisher == "NASA"


def test_external_table_produces_action_and_inaction_states(tmp_path: Path):
    path = tmp_path / "source.csv"
    pd.DataFrame(
        {"record": ["a", "b"], "price": [10, None], "quality": [90, 80], "delay": [1, 2]}
    ).to_csv(path, index=False)
    frame = pd.read_csv(path)
    matrix = to_decision_matrix(frame, id_column="record")
    assert matrix["X"].shape == (2, 3)
    assert matrix["Sigma"][1, 0] == "I"
    assert matrix["missing_cells"] == 1


def test_provenance_records_hash_and_missingness(tmp_path: Path):
    path = tmp_path / "source.csv"
    pd.DataFrame({"id": ["a"], "x": [1], "y": [None]}).to_csv(path, index=False)
    record = build_provenance(
        "ted_open_data",
        path,
        missingness_observed_or_injected="observed",
        outcome_definition="award outcome if present",
    )
    assert len(record.sha256) == 64
    assert record.missing_cells == 1
    assert record.row_count == 1


def test_provenance_rejects_unclassified_missingness(tmp_path: Path):
    path = tmp_path / "source.csv"
    pd.DataFrame({"id": ["a"], "x": [1], "y": [2]}).to_csv(path, index=False)
    with pytest.raises(ValueError, match="missingness_observed_or_injected"):
        build_provenance("nasa_phm", path, missingness_observed_or_injected="guessed", outcome_definition="")
