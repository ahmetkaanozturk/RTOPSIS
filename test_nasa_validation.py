"""NASA C-MAPSS FD001 doğrulama ve stres testi testleri."""
import pytest
from src.rcz_topsis.nasa_validation import (
    NASA_GROUNDED_TYPES,
    validate_nasa_health_ranking,
    run_nasa_missingness_benchmark,
)
from src.rcz_topsis.types import CritType


def test_nasa_health_ranking_physics_grounding():
    """Fizik temelli yönlerin pozitif RUL korelasyonu ve belirgin ayrışma sağladığını test eder."""
    res = validate_nasa_health_ranking(bootstrap_reps=200, seed=42)
    assert res["n_engines"] == 100
    assert res["spearman_rho"] > 0.55
    assert res["spearman_pvalue"] < 1e-8
    assert res["kendall_tau"] > 0.35
    assert res["spearman_rho_inverted_baseline"] < -0.55

    ci_low, ci_high = res["bootstrap_rho_ci95"]
    assert ci_low < res["spearman_rho"] < ci_high
    assert ci_low > 0.40

    top_mean = res["top_10"]["mean_rul"]
    bottom_mean = res["bottom_10"]["mean_rul"]
    assert top_mean > 100.0
    assert bottom_mean < 50.0
    assert top_mean > bottom_mean + 50.0


def test_nasa_criteria_directions_conform_to_physics():
    """Termodinamik aşınma göstergelerinin (gaz sıcaklıkları) COST olarak tanımlandığını teyit eder."""
    assert NASA_GROUNDED_TYPES[0] == CritType.COST     # final_cycle
    assert NASA_GROUNDED_TYPES[1] == CritType.COST     # LPC T24
    assert NASA_GROUNDED_TYPES[2] == CritType.COST     # HPC T30
    assert NASA_GROUNDED_TYPES[3] == CritType.COST     # LPT T50
    assert NASA_GROUNDED_TYPES[4] == CritType.BENEFIT  # HPC P30
    assert NASA_GROUNDED_TYPES[5] == CritType.COST     # HPC Ps30


def test_nasa_missingness_benchmark_runs():
    """Gerçek veri benchmark hattının hatasız çalıştığını ve metrik ürettiğini doğrular."""
    rows = run_nasa_missingness_benchmark(
        losses=(0.20,),
        mechanisms=("mcar", "mnar"),
        reps=4,
        seed=123,
    )
    assert len(rows) > 0
    mcar_rows = [r for r in rows if r["mekanizma"] == "MCAR"]
    mnar_rows = [r for r in rows if r["mekanizma"] == "MNAR"]
    assert len(mcar_rows) == 6
    assert len(mnar_rows) == 6

    for row in rows:
        assert 0.0 <= row["kayip"] <= 1.0
        assert "rho_gt" in row
        assert "rho_rul" in row
        if row["yontem"] != "rcz":
            assert "rho_gt_delta_pvalue_holm" in row
            assert 0.0 <= row["rho_gt_delta_pvalue_holm"] <= 1.0

