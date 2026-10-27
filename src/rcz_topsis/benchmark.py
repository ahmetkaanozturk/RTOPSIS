"""Tekrarlanabilir karşılaştırma deneyi (Monte Carlo).

Protokol:
  1. Tam veri matrisi X (U[10,100]) üretilir; referans sıralama = tam veride klasik TOPSIS.
  2. Kayıp mekanizması uygulanır:
       - MCAR: her hücre bağımsız olarak `loss` olasılıkla eksik.
       - MNAR (maliyet gizleme): MCAR'a ek olarak, gerçek maliyet değeri sütunun
         üst çeyreğinde (>= %75 yüzdelik) olan hücreler 0.5 olasılıkla gizlenir.
       - MAR: eksiklik, başka bir gözlemlenen fayda kriterinin yüksek değerine
         bağlı olarak oluşturulur; gizlenen hücrenin kendi değeri doğrudan
         kullanılmaz.
  3. Her yöntemin eksik matris üzerindeki sıralaması referansla Spearman rho ve
     Kendall tau ile karşılaştırılır. Ortalama ve %95 güven aralığı raporlanır.
Yöntemler:
  - klasik_sifir:     eksik = 0 ile klasik TOPSIS (literatürdeki naif yaklaşım)
  - klasik_ortalama:  eksik = sütun ortalaması ile klasik TOPSIS (imputation)
  - klasik_en_kotu:   eksik faydayı sütun minimumu, eksik maliyeti maksimumu kabul eder
  - topsis_yerel:     her alternatif için gözlenen kriterlerde yerel ağırlıklı TOPSIS
  - alt_uzay:         R-CZ, alpha=0 (ceza yok)  == v0.3 (sqrt(m/m*) etkisiz)
  - rcz:              R-CZ v1.1, alpha=0.5 (global ağırlık + asimetrik ceza)
  - rcz_yerel_v10:    R-CZ v1.0, yerel ağırlıklandırma, alpha=0.5
Not: Bu sentetik bir deneydir; gerçek dünya performansı hakkında tek başına kanıt değildir.
MAR/MNAR mekanizmaları varsayımsal veri üretim protokolleridir ve kurumsal
verideki gerçek kayıp sürecinin yerini tutmaz.
"""
from typing import Dict, List

import numpy as np
from scipy.stats import kendalltau, spearmanr

try:
    from .core import RCZTOPSIS
    from .types import CritType, RCZConfig
except ImportError:
    from src.rcz_topsis.core import RCZTOPSIS
    from src.rcz_topsis.types import CritType, RCZConfig

B, C = CritType.BENEFIT, CritType.COST
DEFAULT_WEIGHTS = np.array([0.25, 0.20, 0.20, 0.15, 0.10, 0.10])
DEFAULT_TYPES = [B, B, C, B, C, B]
METHODS = [
    "klasik_sifir",
    "klasik_ortalama",
    "klasik_en_kotu",
    "topsis_yerel",
    "alt_uzay",
    "rcz",
    "rcz_yerel_v10",
]
STAT_REPS = 2000


def _holm_adjust(pvalues: List[float]) -> List[float]:
    """Return Holm step-down adjusted p-values in the original order."""
    if not pvalues:
        return []
    order = np.argsort(np.asarray(pvalues, dtype=float))
    adjusted = np.empty(len(pvalues), dtype=float)
    running_max = 0.0
    total = len(pvalues)
    for rank, index in enumerate(order):
        value = min(1.0, (total - rank) * float(pvalues[index]))
        running_max = max(running_max, value)
        adjusted[index] = running_max
    return adjusted.tolist()


def _paired_statistics(
    reference: np.ndarray,
    candidate: np.ndarray,
    rng: np.random.Generator,
    reps: int = STAT_REPS,
) -> Dict[str, float]:
    """Bootstrap CI and paired sign-flip p-value for a method difference."""
    differences = np.asarray(candidate, dtype=float) - np.asarray(reference, dtype=float)
    if differences.size == 0:
        return {
            "mean": float("nan"),
            "ci95": float("nan"),
            "ci95_low": float("nan"),
            "ci95_high": float("nan"),
            "pvalue": float("nan"),
        }
    observed = float(np.mean(differences))
    bootstrap_indices = rng.integers(0, differences.size, size=(reps, differences.size))
    bootstrap_means = differences[bootstrap_indices].mean(axis=1)
    ci_low, ci_high = np.quantile(bootstrap_means, [0.025, 0.975])
    signs = rng.choice(np.array([-1.0, 1.0]), size=(reps, differences.size))
    null_means = (differences * signs).mean(axis=1)
    pvalue = float((np.count_nonzero(np.abs(null_means) >= abs(observed)) + 1) / (reps + 1))
    return {
        "mean": observed,
        "ci95": float(max(abs(observed - ci_low), abs(ci_high - observed))),
        "ci95_low": float(ci_low),
        "ci95_high": float(ci_high),
        "pvalue": pvalue,
    }


def classic_topsis(X: np.ndarray, weights: np.ndarray, crit_types) -> np.ndarray:
    norm = np.sqrt(np.sum(X ** 2, axis=0))
    norm[norm == 0] = 1.0
    V = X / norm * weights
    is_b = np.array([ct == B for ct in crit_types])
    vp = np.where(is_b, V.max(0), V.min(0))
    vm = np.where(is_b, V.min(0), V.max(0))
    dp = np.sqrt(((V - vp) ** 2).sum(1))
    dm = np.sqrt(((V - vm) ** 2).sum(1))
    denom = dp + dm
    return np.where(denom > 1e-12, dm / np.maximum(denom, 1e-12), 0.5)


def impute(X: np.ndarray, mask: np.ndarray, how: str) -> np.ndarray:
    Xi = X.copy()
    for j in range(X.shape[1]):
        obs = X[mask[:, j], j]
        Xi[~mask[:, j], j] = 0.0 if how == "zero" else (obs.mean() if obs.size else 0.0)
    return Xi


def _worst_case_impute(X: np.ndarray, mask: np.ndarray, crit_types) -> np.ndarray:
    """Impute missing cells with the observed worst value for that criterion.

    This is a transparent stress baseline, not a claim that all literature
    implementations use this exact rule.
    """
    Xi = X.copy()
    for j, kind in enumerate(crit_types):
        obs = X[mask[:, j], j]
        if obs.size:
            fill = float(np.min(obs) if kind == B else np.max(obs))
        else:
            fill = 0.0
        Xi[~mask[:, j], j] = fill
    return Xi


def _local_topsis_scores(X, mask, w, ct) -> np.ndarray:
    """Observed-subspace TOPSIS with per-alternative renormalized weights.

    This is a directly reproducible partial-information baseline. It is kept
    separate from R-CZ because it has no coverage gate or epistemic penalty.
    """
    n, _ = X.shape
    norm = np.sqrt(np.sum(np.where(mask, X, 0.0) ** 2, axis=0))
    norm[norm == 0] = 1.0
    V = np.where(mask, X / norm * w, 0.0)
    is_b = np.array([kind == B for kind in ct])
    observed = np.where(mask, V, np.nan)
    column_max = np.nanmax(observed, axis=0)
    column_min = np.nanmin(observed, axis=0)
    ideal = np.where(is_b, column_max, column_min)
    anti = np.where(is_b, column_min, column_max)
    scores = np.zeros(n)
    for i in range(n):
        active = mask[i]
        local_weight = w[active] / np.sum(w[active])
        dp = np.sqrt(np.sum(local_weight * (V[i, active] - ideal[active]) ** 2))
        dm = np.sqrt(np.sum(local_weight * (V[i, active] - anti[active]) ** 2))
        scores[i] = dm / (dp + dm) if dp + dm > 1e-12 else 0.5
    return scores


def _rcz_scores(X, mask, w, ct, **cfg) -> np.ndarray:
    sigma = np.where(mask, "A", "I")
    res = RCZTOPSIS(RCZConfig(w_threshold=0.0, min_active_criteria=1, **cfg)).fit_predict(X, sigma, w, ct)
    return np.array([r.score for r in sorted(res, key=lambda r: r.index)])


def method_scores(X, mask, w, ct) -> Dict[str, np.ndarray]:
    return {
        "klasik_sifir": classic_topsis(impute(X, mask, "zero"), w, ct),
        "klasik_ortalama": classic_topsis(impute(X, mask, "mean"), w, ct),
        "klasik_en_kotu": classic_topsis(_worst_case_impute(X, mask, ct), w, ct),
        "topsis_yerel": _local_topsis_scores(X, mask, w, ct),
        "alt_uzay": _rcz_scores(X, mask, w, ct, alpha=0.0),
        "rcz": _rcz_scores(X, mask, w, ct, alpha=0.5),
        "rcz_yerel_v10": _rcz_scores(X, mask, w, ct, alpha=0.5, local_reweighting=True),
    }


def make_mask(X, loss, mechanism, ct, rng) -> np.ndarray:
    n, m = X.shape
    mechanism = mechanism.lower()
    if mechanism not in {"mcar", "mar", "mnar"}:
        raise ValueError(f"Unsupported missingness mechanism: {mechanism}")
    mask = rng.random((n, m)) > loss
    if mechanism == "mnar":
        for j in range(m):
            if ct[j] == C:
                high = X[:, j] >= np.quantile(X[:, j], 0.75)
                mask[high & (rng.random(n) < 0.5), j] = False
    elif mechanism == "mar":
        # Missingness depends on an observed benefit criterion, not on the
        # value of the cell being hidden.
        driver = next((j for j, kind in enumerate(ct) if kind == B), None)
        if driver is not None:
            high_driver = X[:, driver] >= np.quantile(X[:, driver], 0.75)
            for j in range(m):
                if j == driver:
                    continue
                extra_probability = np.where(high_driver, 0.5, 0.1)
                mask[:, j] &= rng.random(n) >= extra_probability
    for i in range(n):  # her adayda en az 2 gözlem
        if mask[i].sum() < 2:
            mask[i, rng.choice(m, 2, replace=False)] = True
    for j in range(m):  # her sütunda en az 2 gözlem
        if mask[:, j].sum() < 2:
            mask[rng.choice(n, 2, replace=False), j] = True
    return mask


def run_benchmark(
    losses=(0.1, 0.3, 0.5),
    mechanisms=("mcar", "mnar"),
    reps: int = 200,
    n_alts: int = 20,
    weights: np.ndarray = DEFAULT_WEIGHTS,
    crit_types=DEFAULT_TYPES,
    seed: int = 42,
) -> List[dict]:
    rng = np.random.default_rng(seed)
    rows = []
    for mech in mechanisms:
        for loss in losses:
            rho = {k: [] for k in METHODS}
            tau = {k: [] for k in METHODS}
            for _ in range(reps):
                X = rng.uniform(10, 100, (n_alts, len(weights)))
                gt = classic_topsis(X, weights, crit_types)
                mask = make_mask(X, loss, mech, crit_types, rng)
                for k, s in method_scores(X, mask, weights, crit_types).items():
                    rho[k].append(spearmanr(gt, s)[0])
                    tau[k].append(kendalltau(gt, s)[0])
            for k in METHODS:
                r = np.array(rho[k]); t = np.array(tau[k])
                rho_stats = _paired_statistics(rho["rcz"], r, rng)
                tau_stats = _paired_statistics(tau["rcz"], t, rng)
                rows.append({
                    "mekanizma": mech.upper(), "kayip": loss, "yontem": k,
                    "rho": r.mean(), "rho_ci95": 1.96 * r.std(ddof=1) / np.sqrt(reps),
                    "tau": t.mean(), "tau_ci95": 1.96 * t.std(ddof=1) / np.sqrt(reps),
                    "rho_delta_vs_rcz": rho_stats["mean"],
                    "rho_delta_ci95": rho_stats["ci95"],
                    "rho_delta_ci95_low": rho_stats["ci95_low"],
                    "rho_delta_ci95_high": rho_stats["ci95_high"],
                    "rho_delta_pvalue": rho_stats["pvalue"],
                    "tau_delta_vs_rcz": tau_stats["mean"],
                    "tau_delta_ci95": tau_stats["ci95"],
                    "tau_delta_ci95_low": tau_stats["ci95_low"],
                    "tau_delta_ci95_high": tau_stats["ci95_high"],
                    "tau_delta_pvalue": tau_stats["pvalue"],
                })
    for mechanism in {row["mekanizma"] for row in rows}:
        mechanism_rows = [
            row for row in rows
            if row["mekanizma"] == mechanism and row["yontem"] != "rcz"
        ]
        for metric in ("rho", "tau"):
            adjusted = _holm_adjust([
                row[f"{metric}_delta_pvalue"] for row in mechanism_rows
            ])
            for row, adjusted_pvalue in zip(mechanism_rows, adjusted):
                row[f"{metric}_delta_pvalue_holm"] = adjusted_pvalue
    return rows


if __name__ == "__main__":
    import pandas as pd
    df = pd.DataFrame(run_benchmark())
    pd.set_option("display.width", 160)
    print(df.round(3).to_string(index=False))
