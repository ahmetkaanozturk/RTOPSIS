"""R-CZ-TOPSIS v1.1 değişmez (invariant) testleri.

Her test motoru (RCZTOPSIS) gerçekten çağırır; formülü testin içinde yeniden
hesaplayıp kendisiyle karşılaştıran totolojik test yoktur.
"""
import numpy as np
import pytest

from src.rcz_topsis.benchmark import classic_topsis
from src.rcz_topsis.core import RCZTOPSIS
from src.rcz_topsis.types import AlternativeStatus, CritType, RCZConfig

B, C = CritType.BENEFIT, CritType.COST


def scores(results):
    return np.array([r.score for r in sorted(results, key=lambda r: r.index)])


def by_idx(results):
    return {r.index: r for r in results}


# ---------------------------------------------------------------- Kural 1
def test_gatekeeper_eliminates_low_coverage():
    X = np.array([[10, 20, 30, 40], [10, 20, 50, 60], [10, 20, 20, 20.]])
    S = np.array([list("AAII"), list("IIAA"), list("IIAA")])
    w = np.array([0.20, 0.20, 0.30, 0.30])
    r = by_idx(RCZTOPSIS(RCZConfig(w_threshold=0.5)).fit_predict(X, S, w, [B] * 4))
    assert r[0].status == AlternativeStatus.INSUFFICIENT_DATA and r[0].score == 0.0
    assert r[0].rank == 3  # elenen en alta
    assert r[1].status == r[2].status == AlternativeStatus.EVALUATED


def test_gatekeeper_requires_min_criteria():
    X = np.array([[10, 20, 30], [15, 25, 35], [12, 22, 32.]])
    S = np.array([list("AII"), list("AAA"), list("AAA")])
    w = np.array([0.60, 0.20, 0.20])  # aday 0: W=0.60 ama m*=1
    r = by_idx(RCZTOPSIS(RCZConfig(w_threshold=0.5, min_active_criteria=2)).fit_predict(X, S, w, [B] * 3))
    assert r[0].status == AlternativeStatus.INSUFFICIENT_DATA


def test_gatekeeper_float_tolerance():
    """W_i = 0.5 olan aday, eşik ondalık gürültüyle 0.5'ten çok az büyük olsa da elenmemeli."""
    X = np.array([[1, 2, 3, 4], [2, 3, 4, 5], [3, 1, 2, 2.]])
    S = np.array([list("AAII"), list("AAAA"), list("AAAA")])
    w = np.array([0.25, 0.25, 0.25, 0.25])
    r = by_idx(RCZTOPSIS(RCZConfig(w_threshold=0.5 + 1e-12)).fit_predict(X, S, w, [B] * 4))
    assert r[0].status == AlternativeStatus.EVALUATED


# ---------------------------------------------------------------- Kural 3
@pytest.mark.parametrize("alpha", [0.0, 0.5, 1.2])
def test_full_data_equals_classic_topsis(alpha):
    """Eksik veri yoksa W_i=1, Gamma=1 -> her alpha için klasik TOPSIS ile aynı skor."""
    rng = np.random.default_rng(123)
    X = rng.uniform(20, 150, (8, 5))
    w = np.array([0.25, 0.20, 0.15, 0.20, 0.20])
    ct = [B, C, B, C, B]
    got = scores(RCZTOPSIS(RCZConfig(alpha=alpha)).fit_predict(X, np.full(X.shape, "A"), w, ct))
    np.testing.assert_allclose(got, classic_topsis(X, w, ct), atol=1e-10)


def test_reproduces_v03_paper_base_scores():
    """Makale Tablo 3 verisinde C_base, v0.3 kodunun (alpha=0) çıktısıyla aynı olmalı.
    Bu, v0.3'teki sqrt(m/m*) çarpanının C* üzerinde etkisiz olduğunu da doğrular."""
    X = np.array([[8, 5000, 16, 10], [9, 7000, 0, 12], [6, 3000, 8, 0], [7, 4500, 32, 6], [10, 8000, 0, 0.]])
    S = np.array([list("AAAA"), list("AAIA"), list("AAAI"), list("AAAA"), list("AAII")])
    res = sorted(RCZTOPSIS().fit_predict(X, S, [0.25] * 4, [B, C, B, B]), key=lambda r: r.index)
    v03 = [0.4571, 0.5615, 0.3589, 0.6333, 0.3629]  # cz_topsis_ekirdek_python_kodu.py çıktısı
    np.testing.assert_allclose([r.base_score for r in res], v03, atol=5e-5)


def test_no_discrimination_gives_neutral_score():
    X = np.full((3, 3), 7.0)
    res = RCZTOPSIS(RCZConfig(alpha=0.0)).fit_predict(X, np.full(X.shape, "A"), [1, 1, 1], [B, C, B])
    assert all(np.isclose(r.score, 0.5) for r in res)


# ------------------------------------------------- Denetim bulgusu 1.2 (v1.1 düzeltmesi)
IDENT_X = np.array([[50, 50, 50, 50], [50, 50, 50, 50], [30, 30, 30, 30], [70, 70, 70, 70.]])
IDENT_S = np.full(IDENT_X.shape, "A")
IDENT_S[1, 3] = "I"


def test_missing_data_is_not_rewarded():
    """Aynı değerlere sahip iki adaydan verisi eksik olan, tam olanı geçmemeli."""
    r0 = by_idx(RCZTOPSIS(RCZConfig(alpha=0.0)).fit_predict(IDENT_X, IDENT_S, [0.25] * 4, [B] * 4))
    assert np.isclose(r0[1].score, r0[0].score)  # cezasızken eşit
    r5 = by_idx(RCZTOPSIS(RCZConfig(alpha=0.5)).fit_predict(IDENT_X, IDENT_S, [0.25] * 4, [B] * 4))
    assert r5[1].score < r5[0].score            # cezayla geride


def test_local_reweighting_v10_bias_is_documented():
    """v1.0 yerel ağırlıklandırması eksik veriyi ödüllendiriyordu; bu yüzden varsayılan değil."""
    r = by_idx(RCZTOPSIS(RCZConfig(alpha=0.0, local_reweighting=True)).fit_predict(IDENT_X, IDENT_S, [0.25] * 4, [B] * 4))
    assert r[1].score > r[0].score


# ---------------------------------------------------------------- Kural 4
COST_X = np.array([[50, 50, 50, 50], [50, 50, 50, 50], [30, 30, 30, 30.]])
COST_S = np.array([list("AIAA"), list("IAAA"), list("AAAA")])  # 0: maliyet gizli, 1: fayda gizli
COST_CT = [B, C, B, B]


def test_gamma_formula_and_cost_asymmetry():
    r = by_idx(RCZTOPSIS(RCZConfig(alpha=0.5)).fit_predict(COST_X, COST_S, [0.25] * 4, COST_CT))
    assert np.isclose(r[0].penalty_gamma, 0.75 ** (0.5 * 1.25))
    assert np.isclose(r[1].penalty_gamma, 0.75 ** (0.5 * 1.00))
    assert r[0].penalty_gamma < r[1].penalty_gamma


@pytest.mark.xfail(strict=True, reason=(
    "BİLİNEN SINIRLAMA (denetim 1.3): Asimetrik ceza, maliyet gizlemenin sağladığı "
    "avantajı karşılayamıyor; maliyetini gizleyen aday yine 1. oluyor. Formül bunu "
    "çözecek şekilde değiştirilirse bu test geçer ve xfail kaldırılmalıdır."))
def test_cost_hiding_does_not_pay_off():
    r = by_idx(RCZTOPSIS(RCZConfig(alpha=0.5)).fit_predict(COST_X, COST_S, [0.25] * 4, COST_CT))
    assert r[0].score <= r[1].score


# ---------------------------------------------------------------- Girdi doğrulama
@pytest.mark.parametrize("kwargs", [
    dict(weights=[0.5, 0.5]),                     # ağırlık boyutu yanlış
    dict(weights=[0.5, 0.5, -0.1]),               # negatif ağırlık
    dict(weights=[0.5, np.nan, 0.5]),             # NaN ağırlık
    dict(weights=[0.5, np.inf, 0.5]),             # sonsuz (inf) ağırlık
    dict(weights=[0.0, 0.0, 0.0]),                # sıfır ağırlık toplamı
    dict(Sigma=np.full((2, 2), "A")),             # Sigma boyutu yanlış
    dict(Sigma=np.array([["A", "GEÇERSİZ", "I"], ["A", "A", "I"]])),  # Bozuk Sigma değeri
    dict(names=["SadeceBirAday"]),                # Alternatif sayısıyla uyuşmayan isim listesi
    dict(X=np.array([[np.nan, 10, 20], [10, 20, 30]])),  # Aktif hücrede NaN
    dict(X=np.array([[np.inf, 10, 20], [10, 20, 30]])),  # Aktif hücrede inf
    dict(X=np.ones((2, 1)), Sigma=np.full((2, 1), "A"), weights=[1.0], crit_types=[B]),  # Tek kriter (< 2)
    dict(X=np.empty((0, 3)), Sigma=np.empty((0, 3)), weights=[1, 1, 1], crit_types=[B, B, B]),  # Boş matris
])
def test_input_validation(kwargs):
    args = dict(X=np.ones((2, 3)), Sigma=np.full((2, 3), "A"), weights=[1, 1, 1], crit_types=[B, B, B])
    args.update(kwargs)
    with pytest.raises(ValueError):
        RCZTOPSIS().fit_predict(**args)


@pytest.mark.parametrize("cfg_kwargs", [
    dict(threshold_tol=float("nan")),
    dict(threshold_tol=-1e-5),
    dict(threshold_tol=float("inf")),
    dict(alpha=-0.5),
    dict(alpha=float("nan")),
    dict(w_threshold=1.5),
    dict(w_threshold=-0.1),
    dict(eps=0.0),
    dict(eps=-1.0),
    dict(min_active_criteria=0),
])
def test_config_validation(cfg_kwargs):
    cfg = RCZConfig(**cfg_kwargs)
    with pytest.raises(ValueError):
        RCZTOPSIS(cfg).fit_predict(np.ones((2, 2)), np.full((2, 2), "A"), [1, 1], [B, C])


# ------------------------------------------------ v1.1 Kanonik Formülasyon ve Değişmezlikler
def test_default_config_local_reweighting_is_false():
    """R-CZ-TOPSIS v1.1'in varsayılan ağırlıklandırma kuralı global alt-uzaydır (local_reweighting=False)."""
    cfg = RCZConfig()
    assert cfg.local_reweighting is False, "v1.1 varsayılanı local_reweighting=False olmalıdır!"


def test_v11_global_weighting_matrix_formulation():
    """v1.1'de aktif hücrelerin V matrisi V_ij = w_j * (x_ij / S_j) formülünü tam olarak karşılar."""
    X = np.array([
        [10.0, 20.0, 30.0],
        [15.0, 25.0, 35.0],
    ])
    Sigma = np.array([
        ["A", "A", "I"],
        ["A", "A", "A"],
    ])
    weights = [0.2, 0.3, 0.5]
    crit_types = [B, B, B]

    engine = RCZTOPSIS(RCZConfig(local_reweighting=False))
    results, expl = engine.explain(X, Sigma, weights, crit_types)

    # 1. Norm paydaları S_j
    s0 = np.sqrt(10.0**2 + 15.0**2)
    s1 = np.sqrt(20.0**2 + 25.0**2)
    s2 = np.sqrt(35.0**2)  # Yalnızca aktif hücre

    assert np.isclose(expl.S[0], s0)
    assert np.isclose(expl.S[1], s1)
    assert np.isclose(expl.S[2], s2)

    # 2. V matrisi kontrolü (Global: V_ij = w_j * r_ij, 1/W_i ile bölünmez!)
    w_norm = np.array(weights) / np.sum(weights)
    expected_v00 = w_norm[0] * (10.0 / s0)
    expected_v01 = w_norm[1] * (20.0 / s1)
    assert np.isclose(expl.V[0, 0], expected_v00)
    assert np.isclose(expl.V[0, 1], expected_v01)
    assert np.isnan(expl.V[0, 2])  # İnaktif hücre NaN olmalı


def test_historical_v10_local_reweighting_separation():
    """v1.0 (local_reweighting=True) tarihsel bir moddur ve v1.1 global ağırlıklandırma ile farklı sonuçlar üretir."""
    X = np.array([
        [10.0, 20.0, 30.0],
        [15.0, 25.0, 35.0],
        [12.0, 22.0, 32.0],
    ])
    Sigma = np.array([
        ["A", "A", "I"],
        ["A", "A", "A"],
        ["A", "I", "A"],
    ])
    weights = [0.3, 0.3, 0.4]
    crit_types = [B, B, B]

    v11_engine = RCZTOPSIS(RCZConfig(local_reweighting=False))
    v10_engine = RCZTOPSIS(RCZConfig(local_reweighting=True))

    res_11 = v11_engine.fit_predict(X, Sigma, weights, crit_types)
    res_10 = v10_engine.fit_predict(X, Sigma, weights, crit_types)

    # Eksik verili adayın (indeks 0) taban skoru iki yöntemde farklı olmalıdır
    assert not np.isclose(res_11[0].base_score, res_10[0].base_score), (
        "v1.0 local reweighting ile v1.1 global reweighting aynı taban skoru üretmemelidir!"
    )


def test_epistemic_reliability_multiplier_invariants():
    """Gamma_i = W_i^(alpha * kappa_i) ve C* = C_base * Gamma_i değişmezlerini doğrular."""
    X = np.array([
        [10.0, 20.0, 30.0],
        [15.0, 25.0, 35.0],
    ])
    # Aday 0: Fayda kriteri eksik, Maliyet kriteri tam
    # Aday 1: Verisi tam
    Sigma = np.array([
        ["I", "A", "A"],
        ["A", "A", "A"],
    ])
    weights = [0.3, 0.3, 0.4]
    crit_types = [B, B, C]  # Kriter 2 maliyettir

    engine = RCZTOPSIS(RCZConfig(alpha=0.5))
    results, expl = engine.explain(X, Sigma, weights, crit_types)

    # Aday 1 (tam veri): W_1 = 1.0 => Gamma_1 = 1.0, C* == C_base
    assert np.isclose(results[1].support_weight, 1.0)
    assert np.isclose(results[1].penalty_gamma, 1.0)
    assert np.isclose(results[1].score, results[1].base_score)

    # Aday 0: C* == C_base * Gamma
    expected_c_star_0 = results[0].base_score * results[0].penalty_gamma
    assert np.isclose(results[0].score, expected_c_star_0)


def test_documentation_and_specification_synchronization():
    """Aktif Markdown/dokümantasyon dosyalarında eski formül ve abartılı iddiaların olmadığını doğrular."""
    from pathlib import Path
    root = Path(__file__).resolve().parent

    active_doc_files = [
        root / "matematiksel_formulasyon.md",
        root / "README.md",
        root / "tubitak_2209_a_proje_oneri_formu.md",
        root / "tubitak_proje_rehberi.md",
        root / "r_cz_matematik.txt",
    ]

    forbidden_phrases = [
        "sqrt(m/m_i*)",
        "sqrt(m / m_i*)",
        "hileyi kesin olarak engeller",
        "maliyet gizleyen aday kazanamaz",
    ]

    for doc_path in active_doc_files:
        if not doc_path.exists():
            continue
        text = doc_path.read_text(encoding="utf-8")
        for phrase in forbidden_phrases:
            assert phrase.lower() not in text.lower(), (
                f"Dosyada yasaklı/eski ifade bulundu: '{phrase}' -> {doc_path.name}"
            )


if __name__ == "__main__":
    pytest.main(["-v", __file__])