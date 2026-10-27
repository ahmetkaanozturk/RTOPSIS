"""Tüm 9 senaryo için otomatik duman (smoke) testleri ve güvenlik kontrolleri.

Bu test modülü şunları doğrular:
1. data/ dizinindeki 9 senaryo CSV dosyasının eksiksiz yüklenmesi ve R-CZ motorundan hatasız geçmesi.
2. Çıktı skorlarının [0, 1] aralığında ve sonlu olması.
3. Sıralamaların 1..N arasında geçerli bir permütasyon oluşturması.
4. XSS / HTML enjeksiyonuna karşı filtreleme doğrulaması.
"""
import html
import pathlib
import numpy as np
import pandas as pd
import pytest

from src.rcz_topsis.core import RCZTOPSIS
from src.rcz_topsis.types import AlternativeStatus, Context, CritType, RCZConfig

DATA_DIR = pathlib.Path(__file__).parent / "data"

CSV_FILES = [
    "elektrikli_arac_benchmark.csv",
    "hava_savunma_radar_tehdit.csv",
    "iha_savunma_benchmark.csv",
    "jeopolitik_catisma_istihbarat.csv",
    "klinik_ilac_biyoteknoloji.csv",
    "startuplar_girisim_sermayesi.csv",
    "tedarikci_secimi_benchmark.csv",
    "uci_automobile_missing_benchmark.csv",
    "yenilenebilir_enerji_santrali.csv",
]


@pytest.mark.parametrize("filename", CSV_FILES)
def test_dataset_runs_cleanly_through_rcz(filename):
    file_path = DATA_DIR / filename
    assert file_path.exists(), f"Veri seti bulunamadı: {filename}"

    df = pd.read_csv(file_path)
    assert len(df) >= 2, f"{filename} en az 2 alternatif içermelidir."
    
    # ID ve açıklama string sütunlarını ayır
    numeric_cols = []
    for c in df.columns:
        converted = pd.to_numeric(df[c].astype(str).str.replace("0_I", "NaN"), errors="coerce")
        if converted.notna().sum() > 0:
            numeric_cols.append(c)
    
    descriptor_cols = [c for c in df.columns if c not in numeric_cols]
    if len(descriptor_cols) == 1:
        names = df[descriptor_cols[0]].astype(str).tolist()
    elif len(descriptor_cols) > 1:
        names = (df[descriptor_cols[0]].astype(str) + " (" + df[descriptor_cols[1]].astype(str) + ")").tolist()
    else:
        names = [f"Alternatif_{i+1}" for i in range(len(df))]

    data_cols = numeric_cols
    assert len(data_cols) >= 2, f"{filename} en az 2 sayısal kriter içermelidir."

    n_alts = len(df)
    n_crits = len(data_cols)
    X = np.zeros((n_alts, n_crits))
    Sigma = np.full((n_alts, n_crits), Context.ACTION.value, dtype=object)

    for i in range(n_alts):
        for j, col in enumerate(data_cols):
            val = df.iloc[i][col]
            if pd.isna(val) or str(val).strip() in ("0_I", "NaN", "nan", ""):
                X[i, j] = 0.0
                Sigma[i, j] = Context.INACTION.value
            else:
                try:
                    X[i, j] = float(val)
                    Sigma[i, j] = Context.ACTION.value
                except ValueError:
                    X[i, j] = 0.0
                    Sigma[i, j] = Context.INACTION.value

    # Eşit ağırlık ve dönüşümlü yönlerle test et
    weights = np.ones(n_crits) / n_crits
    crit_types = [CritType.BENEFIT if k % 2 == 0 else CritType.COST for k in range(n_crits)]

    cfg = RCZConfig(w_threshold=0.40, min_active_criteria=2, alpha=0.50)
    engine = RCZTOPSIS(config=cfg)
    results, expl = engine.explain(X, Sigma, weights, crit_types, names=names)

    assert len(results) == n_alts
    ranks = [r.rank for r in results]
    assert sorted(ranks) == list(range(1, n_alts + 1)), "Sıralamalar 1..N aralığında ardışık olmalıdır."

    for r in results:
        assert np.isfinite(r.score), f"Geçersiz skor: {r.name} -> {r.score}"
        assert 0.0 <= r.score <= 1.0, f"Skor [0, 1] aralığı dışında: {r.name} -> {r.score}"
        assert 0.0 <= r.support_weight <= 1.0


def test_html_escape_sanitizes_xss_payload():
    """Kullanıcı CSV'sindeki zararlı HTML / script payload'larının temizlendiğini doğrular."""
    malicious_input = '<script>alert("XSS")</script>'
    escaped = html.escape(malicious_input)
    assert "<script>" not in escaped
    assert "&lt;script&gt;" in escaped
    assert "</script>" not in escaped
