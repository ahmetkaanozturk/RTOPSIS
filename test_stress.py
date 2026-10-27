"""Monte Carlo karşılaştırma testleri (protokol: src/rcz_topsis/benchmark.py).

Yalnızca deneyde gerçekten gözlenen sonuçlar doğrulanır. R-CZ'nin ortalama ile
doldurmayı (klasik_ortalama) veya cezasız alt-uzayı geçtiği İDDİA EDİLMEZ; mevcut
deneylerde geçmemektedir (bkz. denetim raporu).
"""
import numpy as np
import pandas as pd
import pytest

from src.rcz_topsis.benchmark import run_benchmark


@pytest.fixture(scope="module")
def bench():
    df = pd.DataFrame(run_benchmark(losses=(0.1, 0.3, 0.5), reps=80, seed=7))
    print("\n" + df.round(3).to_string(index=False))
    return df


def rho(df, mech, loss, method):
    return float(df[(df.mekanizma == mech) & (df.kayip == loss) & (df.yontem == method)].rho.iloc[0])


@pytest.mark.parametrize("mech", ["MCAR", "MNAR"])
@pytest.mark.parametrize("loss", [0.1, 0.3, 0.5])
def test_rcz_beats_zero_imputation(bench, mech, loss):
    assert rho(bench, mech, loss, "rcz") > rho(bench, mech, loss, "klasik_sifir")


@pytest.mark.parametrize("mech", ["MCAR", "MNAR"])
@pytest.mark.parametrize("loss", [0.3, 0.5])
def test_v11_not_worse_than_v10_at_moderate_loss(bench, mech, loss):
    assert rho(bench, mech, loss, "rcz") >= rho(bench, mech, loss, "rcz_yerel_v10")


def test_results_are_reproducible():
    a = run_benchmark(losses=(0.3,), mechanisms=("mcar",), reps=10, seed=1)
    b = run_benchmark(losses=(0.3,), mechanisms=("mcar",), reps=10, seed=1)
    assert np.allclose([r["rho"] for r in a], [r["rho"] for r in b])


def test_mar_is_supported_and_reproducible():
    rows = run_benchmark(losses=(0.3,), mechanisms=("mar",), reps=10, seed=11)
    assert {row["mekanizma"] for row in rows} == {"MAR"}
    assert all(np.isfinite(row["rho"]) and np.isfinite(row["tau"]) for row in rows)


def test_unknown_missingness_mechanism_is_rejected():
    with pytest.raises(ValueError, match="Unsupported missingness mechanism"):
        run_benchmark(losses=(0.3,), mechanisms=("unknown",), reps=1)


def test_literature_comparator_baselines_return_bounded_scores():
    rows = run_benchmark(losses=(0.3,), mechanisms=("mcar",), reps=5, seed=12)
    assert {"klasik_en_kotu", "topsis_yerel"} <= {row["yontem"] for row in rows}
    assert all(0.0 <= row["rho"] <= 1.0 for row in rows)


def test_paired_statistics_are_reported_for_mar_and_mnar():
    rows = run_benchmark(
        losses=(0.3,),
        mechanisms=("mar", "mnar"),
        reps=12,
        seed=21,
    )
    for row in rows:
        assert {
            "rho_delta_vs_rcz",
            "rho_delta_ci95",
            "rho_delta_ci95_low",
            "rho_delta_ci95_high",
            "rho_delta_pvalue",
            "tau_delta_vs_rcz",
            "tau_delta_ci95",
            "tau_delta_ci95_low",
            "tau_delta_ci95_high",
            "tau_delta_pvalue",
        } <= row.keys()
        assert 0.0 < row["rho_delta_pvalue"] <= 1.0
        assert 0.0 <= row["rho_delta_ci95"]
        assert 0.0 < row["tau_delta_pvalue"] <= 1.0


def test_holm_adjustment_is_present_for_each_mar_mnar_comparison():
    rows = run_benchmark(
        losses=(0.1, 0.3),
        mechanisms=("mar", "mnar"),
        reps=8,
        seed=41,
    )
    for row in rows:
        if row["yontem"] == "rcz":
            continue
        assert 0.0 < row["rho_delta_pvalue_holm"] <= 1.0
        assert row["rho_delta_pvalue_holm"] >= row["rho_delta_pvalue"]
        assert 0.0 < row["tau_delta_pvalue_holm"] <= 1.0
        assert row["tau_delta_pvalue_holm"] >= row["tau_delta_pvalue"]


def test_paired_statistics_are_reproducible():
    kwargs = {"losses": (0.3,), "mechanisms": ("mnar",), "reps": 8, "seed": 31}
    a = run_benchmark(**kwargs)
    b = run_benchmark(**kwargs)
    assert np.allclose(
        [row["rho_delta_pvalue"] for row in a],
        [row["rho_delta_pvalue"] for row in b],
    )


if __name__ == "__main__":
    pytest.main(["-v", "-s", __file__])