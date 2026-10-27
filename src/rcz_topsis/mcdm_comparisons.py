"""Çok Kriterli Karar Verme (MCDM) karşılaştırma motoru ve yöntem analizleri.

Desteklenen Karşılaştırmalı Yöntemler:
1. R-CZ-TOPSIS (v1.1 - Alt-Uzay İzdüşümü ve Asimetrik Epistemik Ceza)
2. Klasik TOPSIS (Zero-Imputation, Hwang & Yoon 1981)
3. Ortalama Doldurmalı TOPSIS (Mean-Imputation TOPSIS)
4. VIKOR (Opricovic 1998 - Uzlaşık Çözüm & Q Skoru)
5. PROMETHEE II (Brans & Vincke 1985 - Net Üstünlük Akışı Phi)
6. SAW / WSM (Churchman & Ackoff 1954 - Basit Ağırlıklı Toplam)
7. AHP & ELECTRE (Teorik & Niteliksel Kıyaslama Kütüphanesi; sayısal canlı motor değildir)
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd

try:
    from .types import Context, CritType
except ImportError:
    from src.rcz_topsis.types import Context, CritType


def run_classic_topsis(X: np.ndarray, Sigma: np.ndarray, weights: np.ndarray, crit_types: list) -> Tuple[np.ndarray, List[int]]:
    """Eksik hücreleri 0.0 kabul eden naif Klasik TOPSIS."""
    n, m = X.shape
    X_c = np.where(Sigma == Context.ACTION.value, X, 0.0)
    norm = np.sqrt(np.sum(X_c**2, axis=0))
    norm[norm == 0] = 1.0
    V = (X_c / norm) * weights
    is_b = np.array([ct == CritType.BENEFIT for ct in crit_types])
    vp = np.where(is_b, np.max(V, axis=0), np.min(V, axis=0))
    vm = np.where(is_b, np.min(V, axis=0), np.max(V, axis=0))
    dp = np.sqrt(np.sum((V - vp)**2, axis=1))
    dm = np.sqrt(np.sum((V - vm)**2, axis=1))
    denom = dp + dm
    scores = np.where(denom > 1e-12, dm / np.maximum(denom, 1e-12), 0.5)
    ranks = pd.Series(scores).rank(ascending=False, method="min").astype(int).tolist()
    return scores, ranks


def run_mean_imputation_topsis(X: np.ndarray, Sigma: np.ndarray, weights: np.ndarray, crit_types: list) -> Tuple[np.ndarray, List[int]]:
    """Eksik hücreleri sütunun gözlenen ortalamasıyla dolduran Imputation TOPSIS."""
    n, m = X.shape
    X_m = X.copy()
    for j in range(m):
        obs = X[Sigma[:, j] == Context.ACTION.value, j]
        col_mean = float(np.mean(obs)) if len(obs) > 0 else 0.0
        X_m[Sigma[:, j] != Context.ACTION.value, j] = col_mean
    norm = np.sqrt(np.sum(X_m**2, axis=0))
    norm[norm == 0] = 1.0
    V = (X_m / norm) * weights
    is_b = np.array([ct == CritType.BENEFIT for ct in crit_types])
    vp = np.where(is_b, np.max(V, axis=0), np.min(V, axis=0))
    vm = np.where(is_b, np.min(V, axis=0), np.max(V, axis=0))
    dp = np.sqrt(np.sum((V - vp)**2, axis=1))
    dm = np.sqrt(np.sum((V - vm)**2, axis=1))
    denom = dp + dm
    scores = np.where(denom > 1e-12, dm / np.maximum(denom, 1e-12), 0.5)
    ranks = pd.Series(scores).rank(ascending=False, method="min").astype(int).tolist()
    return scores, ranks


def run_vikor(X: np.ndarray, Sigma: np.ndarray, weights: np.ndarray, crit_types: list, v: float = 0.5) -> Tuple[np.ndarray, List[int]]:
    """VIKOR Uzlaşık Çözüm Sıralama Yöntemi (Q_i indeksi ve 1 - Q_i başarı puanı)."""
    n, m = X.shape
    f_star = np.zeros(m)
    f_minus = np.zeros(m)
    
    for j in range(m):
        obs = X[Sigma[:, j] == Context.ACTION.value, j]
        if len(obs) == 0:
            obs = np.array([1.0])
        if crit_types[j] == CritType.BENEFIT:
            f_star[j] = np.max(obs)
            f_minus[j] = np.min(obs)
        else:
            f_star[j] = np.min(obs)
            f_minus[j] = np.max(obs)
            
    diff_range = np.abs(f_star - f_minus)
    diff_range[diff_range < 1e-12] = 1.0

    S = np.zeros(n)
    R = np.zeros(n)
    for i in range(n):
        terms = np.zeros(m)
        for j in range(m):
            if Sigma[i, j] == Context.ACTION.value:
                dist = abs(f_star[j] - X[i, j]) / diff_range[j]
            else:
                # Eksik veri VIKOR'da en kötü göreli uzaklık (1.0) sayılır
                dist = 1.0
            terms[j] = weights[j] * dist
        S[i] = np.sum(terms)
        R[i] = np.max(terms)

    s_star, s_minus = np.min(S), np.max(S)
    r_star, r_minus = np.min(R), np.max(R)
    s_denom = s_minus - s_star if (s_minus - s_star) > 1e-12 else 1.0
    r_denom = r_minus - r_star if (r_minus - r_star) > 1e-12 else 1.0

    Q = v * ((S - s_star) / s_denom) + (1.0 - v) * ((R - r_star) / r_denom)
    # VIKOR'da Q ne kadar küçükse aday o kadar iyidir. 0-100 ölçeğinde başarı puanı:
    vikor_score = np.clip(1.0 - Q, 0.0, 1.0)
    ranks = pd.Series(Q).rank(ascending=True, method="min").astype(int).tolist()
    return vikor_score, ranks


def run_promethee_ii(X: np.ndarray, Sigma: np.ndarray, weights: np.ndarray, crit_types: list) -> Tuple[np.ndarray, List[int]]:
    """PROMETHEE II Doğrusal Tercih ve Net Akış (Phi = Phi+ - Phi-) Yöntemi."""
    n, m = X.shape
    ranges = np.zeros(m)
    for j in range(m):
        obs = X[Sigma[:, j] == Context.ACTION.value, j]
        r_val = float(np.max(obs) - np.min(obs)) if len(obs) > 0 else 1.0
        ranges[j] = r_val if r_val > 1e-12 else 1.0

    pi_mat = np.zeros((n, n))
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            pair_pref = 0.0
            for j in range(m):
                if Sigma[a, j] == Context.ACTION.value and Sigma[b, j] == Context.ACTION.value:
                    val_a, val_b = X[a, j], X[b, j]
                    diff = (val_a - val_b) if crit_types[j] == CritType.BENEFIT else (val_b - val_a)
                    p_val = max(0.0, diff / ranges[j])
                    pair_pref += weights[j] * p_val
            pi_mat[a, b] = pair_pref

    phi_plus = np.sum(pi_mat, axis=1) / max(1, n - 1)
    phi_minus = np.sum(pi_mat, axis=0) / max(1, n - 1)
    net_phi = phi_plus - phi_minus  # [-1, +1] aralığında
    # 0 - 1 arası ölçekleme:
    promethee_score = np.clip((net_phi + 1.0) / 2.0, 0.0, 1.0)
    ranks = pd.Series(-net_phi).rank(method="min").astype(int).tolist()
    return promethee_score, ranks


def run_saw(X: np.ndarray, Sigma: np.ndarray, weights: np.ndarray, crit_types: list) -> Tuple[np.ndarray, List[int]]:
    """SAW / WSM (Simple Additive Weighting) Doğrusal Ağırlıklı Toplam Yöntemi."""
    n, m = X.shape
    max_vals = np.zeros(m)
    min_vals = np.zeros(m)
    for j in range(m):
        obs = X[Sigma[:, j] == Context.ACTION.value, j]
        max_vals[j] = np.max(obs) if len(obs) > 0 else 1.0
        min_vals[j] = np.min(obs) if len(obs) > 0 else 1.0

    scores = np.zeros(n)
    for i in range(n):
        tot = 0.0
        for j in range(m):
            if Sigma[i, j] == Context.ACTION.value:
                val = X[i, j]
                if crit_types[j] == CritType.BENEFIT:
                    r_ij = val / max_vals[j] if max_vals[j] > 1e-12 else 0.0
                else:
                    r_ij = min_vals[j] / val if val > 1e-12 else 0.0
                tot += weights[j] * r_ij
        scores[i] = tot
    ranks = pd.Series(scores).rank(ascending=False, method="min").astype(int).tolist()
    return scores, ranks


# ==============================================================================
# TÜM MCDM YÖNTEMLERİNİN DERİNLEMESİNE NİTELİKSEL KIYASLAMA BİLGİ BANKASI
# ==============================================================================
MCDM_METHOD_DOSSIERS = {
    "R-CZ-TOPSIS": {
        "tam_ad": "R-CZ-TOPSIS (Rigorous Contextual Zero TOPSIS v1.1)",
        "literatur": "Bu proje içi çalışma adı; hakemli/bağımsız literatür kaydı olarak doğrulanmamıştır.",
        "matematiksel_ozet": r"J_i^* \text{ alt-uzayında } D_i^+, D_i^- \text{ mesafeleri; } \Gamma_i = (W_i)^{\alpha \cdot \kappa_i} \text{ ile asimetrik ceza; } C^* = C_{\text{base}} \times \Gamma_i",
        "rcz_avantajlari": [
            "Tamamen Imputation-Free: Eksik hücrelere hiçbir tahmini ya da sahte sayı uydurmaz.",
            "Hard Gatekeeper: Asgari bilgi eşiğini (%50) geçemeyen adayları otomatik eler.",
            "Asimetrik Maliyet Savunması (κ_i): Maliyet gizleyen adayları üssel olarak cezalandırarak haksız avantajı sınırlandırmayı amaçlar.",
            "Geriye Dönük %100 Analitik Uyumluluk: Veri tam olduğunda Klasik TOPSIS ile birebir özdeştir.",
        ],
        "rcz_sinirlari": [
            "Aşırı katı alpha seçiminde (örn. α=1.2) eksik verili ancak gerçekten çok üstün alternatifler fazla cezalandırılabilir.",
            "Hiyerarşik / nitel kriterlerin anket tabanlı yapılandırılması için ikili karşılaştırma mekanizması içermez.",
        ],
    },
    "Klasik TOPSIS": {
        "tam_ad": "Klasik TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)",
        "literatur": "Hwang, C. L., & Yoon, K. (1981). Multiple Attribute Decision Making. Springer.",
        "matematiksel_ozet": r"D_i^+ = \sqrt{\sum_{j=1}^m (v_{ij} - v_j^+)^2}, \quad C_i = \frac{D_i^-}{D_i^+ + D_i^-}",
        "rcz_ye_gore_avantajlari": [
            "Veri seti tamamen eksiksiz (%100 tam) olduğunda hesaplaması son derece basittir ve O(N × M) sürede çalışır.",
            "Geometrik ideallere (en iyi ve en kötü) olan mesafeyi aynı anda hesaba katan sezgisel bir mantığı vardır.",
        ],
        "rcz_ye_gore_zafiyetleri": [
            "Eksik veriyi doğrudan 0.0 kabul eder veya adayı matristen siler (Listwise deletion).",
            "Haksız İnfaz (False Elimination): Fayda kriteri eksik olan kaliteli bir adayı koordinat orijinine çekerek haksızca eler.",
            "Haksız Ödüllendirme (False Inflation): Maliyet kriterini gizleyen kötü bir adayı 'sıfır maliyetli/bedava' sanarak şampiyon yapabilir.",
            "Hard Gatekeeper koruması yoktur; %10 verisi olan adayı da geçerli sayar.",
        ],
    },
    "Ortalama Imputation TOPSIS": {
        "tam_ad": "Yapay Doldurmalı TOPSIS (Mean Imputation TOPSIS; k-NN uygulanmamıştır)",
        "literatur": "Little, R. J., & Rubin, D. B. (2019). Statistical Analysis with Missing Data. Wiley.",
        "matematiksel_ozet": r"\tilde{X}_{ij} = \text{mean}(X_{\cdot j}) \quad \text{ardından standart TOPSIS}",
        "rcz_ye_gore_avantajlari": [
            "Rastgele kayıp (MCAR) senaryolarında varyans sapması göz ardı edilirse, referans tam sıralamayı yüksek korelasyonla (ρ ≈ 0.78) koruyabilir.",
            "Mevcut klasik yazılımlara hiçbir kod değişikliği yapmadan uygulanabilir.",
        ],
        "rcz_ye_gore_zafiyetleri": [
            "Uydurma Veri Üretir: Karar matrisinde hiç ölçülmemiş değerlerin yerine gerçekte var olmayan sayılar uydurur.",
            "Varyansı Yapay Olarak Düşürür: Hücrelere ortalama yazılması gerçek riskleri gizler ve standart hatayı yanıltıcı biçimde küçültür.",
            "Kasıtlı Hileye Karşı Korumasızdır: Maliyeti çok yüksek olan bir adaya sektör ortalaması atanarak adaya haksız doping yapılmış olur.",
            "Yasal ve Regülatif Denetimlerde Geçersizdir: Savunma veya sağlık ihalelerinde uydurma veriyle karar verilemez.",
        ],
    },
    "VIKOR": {
        "tam_ad": "VIKOR (VlseKriterijumska Optimizacija I Kompromisno Resenje)",
        "literatur": "Opricovic, S. (1998). Multicriteria Optimization of Civil Engineering Systems. Belgrade.",
        "matematiksel_ozet": r"S_i = \sum w_j \frac{f_j^* - f_{ij}}{f_j^* - f_j^-}, \quad R_i = \max_j \left[ w_j \frac{f_j^* - f_{ij}}{f_j^* - f_j^-} \right], \quad Q_i = v \frac{S_i - S^*}{S^- - S^*} + (1-v) \frac{R_i - R^*}{R^- - R^*}",
        "rcz_ye_gore_avantajlari": [
            "Uzlaşık Çözüm Üretir: Çoğunluk faydası (S) ile karşıt görüşlünün maksimum bireysel pişmanlığını (R) dengeleyen benzersiz bir uzlaşma parametresi (v) sunar.",
            "Kabul edilebilir avantaj ve istikrar koşulları (C1, C2) sayesinde birinci olan adayın gerçekten baskın olup olmadığını denetler.",
        ],
        "rcz_ye_gore_zafiyetleri": [
            "Kutup Noktalarına Aşırı Bağımlıdır: f_j^* ve f_j^- değerleri eksik hücrelerden ve uç değerlerden aşırı etkilenir.",
            "Eksik verili hücrelerde pişmanlık (R_i) hesabı çöker; adayın eksik kriteri ya en kötü kabul edilip elenir ya da tanımsız kalır.",
            "Hard Gatekeeper mekanizması yoktur; tekil adil alt-uzay skoru üretmez.",
        ],
    },
    "PROMETHEE II": {
        "tam_ad": "PROMETHEE I & II (Preference Ranking Organization Method for Enrichment Evaluations)",
        "literatur": "Brans, J. P., & Vincke, P. (1985). Management Science, 31(6), 647-656.",
        "matematiksel_ozet": r"\pi(a, b) = \sum w_j P_j(a, b), \quad \Phi(a) = \Phi^+(a) - \Phi^-(a)",
        "rcz_ye_gore_avantajlari": [
            "Kriter bazında 6 farklı tercih fonksiyonu (V-şekilli, basamaklı, gauss vb.) tanımlayarak insan psikolojisindeki farksızlık (q) ve kesin tercih (p) eşiklerini modelleyebilir.",
            "Kriterler arasında dengeleyici olmayan (non-compensatory) katı karşılaştırmalara izin verir.",
        ],
        "rcz_ye_gore_zafiyetleri": [
            "İkili Karşılaştırma Kilidi: İki adaydan birinde ilgili kriter ölçülmemişse d = f(a) - f(b) farkı tanımsız kalır ve tercih akışı kesilir.",
            "Hesaplama Karmaşıklığı Yüksektir: Her kriter için N(N-1) çift karşılaştırma gerekir; O(N² × M) sürede çalışır.",
            "Eksik veriyi cezalandıran asimetrik güvenlik çarpanı ve asgari bilgi barajı yoktur.",
        ],
    },
    "AHP": {
        "tam_ad": "AHP (Analytic Hierarchy Process - Analitik Hiyerarşi Süreci)",
        "literatur": "Saaty, T. L. (1980). The Analytic Hierarchy Process. McGraw-Hill.",
        "matematiksel_ozet": r"A \cdot w = \lambda_{\max} \cdot w, \quad CR = \frac{CI}{RI} < 0.10",
        "rcz_ye_gore_avantajlari": [
            "Niteliksel ve Hiyerarşik Problemlerde Liderdir: Sayısal olmayan sübjektif faktörleri (tasarım, marka prestiji) 1-9 Saaty ölçeğiyle sayısallaştırır.",
            "Tutarlılık Oranı (CR) ile karar vericinin mantıksal çelişkilerini (A>B, B>C ama C>A gibi) yakalar.",
        ],
        "rcz_ye_gore_zafiyetleri": [
            "Aşırı Bilişsel Yük: N aday için N(N-1)/2 adet ikili soru sorulmalıdır. 12 araç için 66 soru, 8 kriter için 28 soru gerekir.",
            "Eksik Veri Karşısında Çöker: İkili matriste tek bir hücrenin bilinmemesi durumunda özvektör (eigenvector) ve tutarlılık matrisi çöker.",
            "Ölçülebilir mühendislik verilerinde yapay anket zorunluluğu getirir.",
        ],
    },
    "ELECTRE Serisi": {
        "tam_ad": "ELECTRE (Elimination and Choice Expressing Reality - Roy 1968)",
        "literatur": "Roy, B. (1968). Revue Française d'Informatique et de Recherche Opérationnelle.",
        "matematiksel_ozet": r"C(a, b) = \sum_{j: g_j(a) \ge g_j(b)} w_j, \quad D(a, b) = \max_j \frac{g_j(b) - g_j(a)}{\text{range}_j}",
        "rcz_ye_gore_avantajlari": [
            "Uyum (Concordance) ve Uyumsuzluk (Discordance) eşikleri ile kesin veto hakkı sağlar; bir kriter çok kötüyse aday diğerleri ne kadar iyi olursa olsun elenebilir.",
        ],
        "rcz_ye_gore_zafiyetleri": [
            "Döngüsel Kilitlenme (Cyclic Intransitivity): A B'yi, B C'yi, C de A'yı yenebilir; tekil bir sıralama üretilemeyebilir.",
            "Eksik veri uyum ve veto eşiklerini tanımsız hale getirir.",
            "Eşik değerlerinin (p, q, v) belirlenmesi sübjektiftir ve uzman müdahalesi gerektirir.",
        ],
    },
    "SAW / WSM": {
        "tam_ad": "SAW (Simple Additive Weighting / Weighted Sum Model)",
        "literatur": "Churchman, C. W., & Ackoff, R. L. (1954). Operations Research.",
        "matematiksel_ozet": r"S_i = \sum_{j=1}^m w_j \cdot r_{ij}",
        "rcz_ye_gore_avantajlari": [
            "Dünyadaki en anlaşılır ve en hızlı çok kriterli toplama yöntemidir.",
        ],
        "rcz_ye_gore_zafiyetleri": [
            "Kriterler arasında tam ikameye (full compensation) izin verir; bir kriterdeki felaket diğerindeki başarıyla örtülebilir.",
            "Eksik hücrelere 0 verilmesi durumunda adayı acımasızca geriye iter; asimetrik güvenlik ceza sistemi yoktur.",
        ],
    },
}
