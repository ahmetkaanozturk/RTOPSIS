"""R-CZ-TOPSIS karar motoru (formülasyon v1.1).

v1.1 değişikliği (denetim sonrası): Varsayılan olarak ideal noktalar ve alt-uzay
mesafeleri GLOBAL ağırlıklarla (w_j) hesaplanır. v1.0'daki yerel ağırlıklandırma
(w'_ij = w_j / W_i), verisi eksik adayların koordinatlarını 1/W_i kat büyüterek
eksik veriyi ödüllendirdiği için varsayılandan kaldırılmış, yalnızca
RCZConfig(local_reweighting=True) ile karşılaştırma amaçlı erişilebilir bırakılmıştır.
"""
import sys
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union

import numpy as np

try:
    from .types import (
        AlternativeResult,
        AlternativeStatus,
        Context,
        CritType,
        RCZConfig,
    )
except ImportError:
    from src.rcz_topsis.types import (
        AlternativeResult,
        AlternativeStatus,
        Context,
        CritType,
        RCZConfig,
    )


@dataclass
class RCZExplanation:
    """Hesaplamanın tüm ara adımları (şeffaflık / raporlama için)."""
    weights: np.ndarray        # Normalize global ağırlıklar (m,)
    active_mask: np.ndarray    # (n, m) bool
    S: np.ndarray              # Sütun norm paydaları (m,)
    W_cov: np.ndarray          # Bilgi kapsama oranı (n,)
    m_active: np.ndarray       # Aktif kriter sayısı (n,)
    valid_gate: np.ndarray     # Gatekeeper sonucu (n,)
    w_eff: np.ndarray          # Kullanılan ağırlıklar (n, m)
    V: np.ndarray              # Ağırlıklı normalize matris, eksik = NaN (n, m)
    v_plus: np.ndarray         # (m,)
    v_minus: np.ndarray        # (m,)
    d_plus: np.ndarray         # (n,) geçersizler için NaN
    d_minus: np.ndarray        # (n,)
    missing_cost: np.ndarray   # (n,)
    kappa: np.ndarray          # (n,)
    gamma: np.ndarray          # (n,)


class RCZTOPSIS:
    """Rigorous Contextual Zero TOPSIS (R-CZ-TOPSIS) Karar Motoru.

    Alt-uzay izdüşümü, Hard Gatekeeper ve asimetrik epistemik risk cezası ile
    eksik verili karar problemlerini, eksik hücrelere değer uydurmadan çözer.
    """

    def __init__(self, config: Optional[RCZConfig] = None):
        self.config = config or RCZConfig()

    # ------------------------------------------------------------------ #
    def explain(
        self,
        X: Union[np.ndarray, list],
        Sigma: Union[np.ndarray, list],
        weights: Union[np.ndarray, list],
        crit_types: List[Union[CritType, str]],
        names: Optional[List[str]] = None,
    ) -> Tuple[List[AlternativeResult], RCZExplanation]:
        cfg = self.config
        X_mat = np.asarray(X, dtype=np.float64)
        Sigma_mat = np.asarray(Sigma)
        w_vec = np.asarray(weights, dtype=np.float64)

        # ---------------- Sıkı Girdi ve Konfigürasyon Doğrulamaları ----------------
        if X_mat.ndim != 2:
            raise ValueError("X matrisi tam olarak iki boyutlu (2D) olmalıdır.")
        n_alts, n_crits = X_mat.shape
        if n_alts < 1:
            raise ValueError("Karar matrisinde en az 1 alternatif (satır) bulunmalıdır.")
        if n_crits < 2:
            raise ValueError(f"Çok kriterli karar analizi (MCDM) için en az 2 kriter gereklidir; {n_crits} kriter verildi.")

        if Sigma_mat.shape != X_mat.shape:
            raise ValueError(f"Sigma boyutu {Sigma_mat.shape}, X boyutu {X_mat.shape} ile eşleşmiyor.")

        valid_sigma_vals = {Context.ACTION.value, Context.INACTION.value, Context.ACTION, Context.INACTION, "A", "I"}
        invalid_sig = set(Sigma_mat.ravel()) - valid_sigma_vals
        if invalid_sig:
            raise ValueError(f"Sigma matrisinde geçersiz bağlam değerleri tespit edildi: {invalid_sig}. Yalnızca 'A' ve 'I' kabul edilir.")

        if w_vec.shape != (n_crits,):
            raise ValueError(f"Ağırlık vektörü boyutu ({w_vec.shape[0]}) kriter sayısıyla ({n_crits}) eşleşmiyor.")
        if not np.all(np.isfinite(w_vec)):
            raise ValueError("Ağırlık vektöründe NaN veya sonsuz (inf) değer bulunamaz.")
        if np.any(w_vec <= 0):
            raise ValueError("Tüm kriter ağırlıkları kesinlikle pozitif (> 0) olmalıdır.")
        w_sum = float(np.sum(w_vec))
        if np.isclose(w_sum, 0.0):
            raise ValueError("Kriter ağırlıklarının toplamı sıfır olamaz.")
        w_vec = w_vec / w_sum

        if len(crit_types) != n_crits:
            raise ValueError(f"crit_types uzunluğu ({len(crit_types)}) kriter sayısıyla ({n_crits}) eşleşmiyor.")

        if names is not None and len(names) != n_alts:
            raise ValueError(f"names listesi uzunluğu ({len(names)}) alternatif sayısı ({n_alts}) ile eşleşmiyor.")

        # Hiperparametre kontrolleri
        if not np.isfinite(cfg.alpha) or cfg.alpha < 0.0:
            raise ValueError(f"alpha parametresi negatif veya tanımsız olamaz: {cfg.alpha}")
        if not (0.0 <= cfg.w_threshold <= 1.0):
            raise ValueError(f"w_threshold parametresi [0.0, 1.0] kapalı aralığında olmalıdır: {cfg.w_threshold}")
        if not np.isfinite(cfg.threshold_tol) or cfg.threshold_tol < 0.0:
            raise ValueError(f"threshold_tol parametresi sonlu ve negatif olmayan bir sayı olmalıdır: {cfg.threshold_tol}")
        if cfg.min_active_criteria < 1:
            raise ValueError(f"min_active_criteria en az 1 olmalıdır: {cfg.min_active_criteria}")
        if cfg.eps <= 0.0 or not np.isfinite(cfg.eps):
            raise ValueError("eps parametresi sıfırdan büyük ve sonlu bir değer olmalıdır.")

        parsed_ct = [CritType(ct) if isinstance(ct, str) else ct for ct in crit_types]
        if names is None:
            names = [f"Alternatif_{i+1}" for i in range(n_alts)]

        active_mask = (Sigma_mat == Context.ACTION.value) | (Sigma_mat == Context.ACTION) | (Sigma_mat == "A")
        if np.any(~np.isfinite(X_mat[active_mask])):
            raise ValueError("Aktif ('A') işaretli veri hücrelerinde NaN veya sonsuz (inf) bulunamaz.")

        col_active_counts = active_mask.sum(axis=0)
        if np.any(col_active_counts == 0):
            empty_cols = np.where(col_active_counts == 0)[0].tolist()
            raise ValueError(f"Şu kriter sütun(lar)ında hiçbir alternatifte aktif ('A') ölçüm bulunamadı: {empty_cols}. Karar matrisinde tamamen boş bir kriter değerlendirilemez.")

        # 1. Sütun norm paydaları (yalnızca aktif ölçümler)
        S = np.ones(n_crits)
        for j in range(n_crits):
            col = X_mat[active_mask[:, j], j]
            norm_val = float(np.sqrt(np.sum(col ** 2))) if col.size else 0.0
            S[j] = norm_val if norm_val > 0 else 1.0

        # 2. Kapsama ve Hard Gatekeeper
        m_active = active_mask.sum(axis=1).astype(int)
        W_cov = np.clip(np.array([float(np.sum(w_vec[active_mask[i]])) for i in range(n_alts)]), 0.0, 1.0)
        valid_gate = (W_cov >= cfg.w_threshold - cfg.threshold_tol) & (m_active >= cfg.min_active_criteria)

        # 3. Ağırlıklar ve V matrisi
        if cfg.local_reweighting:
            w_eff = np.where(W_cov[:, None] > 0, w_vec[None, :] / np.maximum(W_cov[:, None], cfg.eps), 0.0)
        else:
            w_eff = np.tile(w_vec, (n_alts, 1))
        V = np.full((n_alts, n_crits), np.nan)
        use = active_mask & valid_gate[:, None]
        V[use] = (w_eff * X_mat / S[None, :])[use]

        # 4. İdeal / anti-ideal noktalar (yalnızca geçerli adayların aktif hücreleri)
        v_plus = np.zeros(n_crits)
        v_minus = np.zeros(n_crits)
        for j in range(n_crits):
            col = V[:, j][~np.isnan(V[:, j])]
            if col.size == 0:
                continue
            if parsed_ct[j] == CritType.BENEFIT:
                v_plus[j], v_minus[j] = col.max(), col.min()
            else:
                v_plus[j], v_minus[j] = col.min(), col.max()

        # 5. Alt-uzay mesafeleri, asimetrik ceza, skor
        d_plus = np.full(n_alts, np.nan)
        d_minus = np.full(n_alts, np.nan)
        is_cost = np.array([ct == CritType.COST for ct in parsed_ct])
        missing_cost = np.array([float(np.sum(w_vec[(~active_mask[i]) & is_cost])) for i in range(n_alts)])
        kappa = 1.0 + missing_cost
        gamma = np.where(valid_gate, W_cov ** (cfg.alpha * kappa), 0.0)

        results: List[AlternativeResult] = []
        for i in range(n_alts):
            if not valid_gate[i]:
                results.append(AlternativeResult(
                    index=i, name=names[i], score=0.0, base_score=0.0,
                    support_weight=float(W_cov[i]), penalty_gamma=0.0,
                    active_criteria_count=int(m_active[i]),
                    status=AlternativeStatus.INSUFFICIENT_DATA,
                ))
                continue
            idx = np.where(active_mask[i])[0]
            d_plus[i] = float(np.sqrt(np.sum((V[i, idx] - v_plus[idx]) ** 2)))
            d_minus[i] = float(np.sqrt(np.sum((V[i, idx] - v_minus[idx]) ** 2)))
            denom = d_plus[i] + d_minus[i]
            # Ayırt edicilik yoksa (ideal = anti-ideal) nötr skor 0.5
            c_base = 0.5 if denom < cfg.eps else float(d_minus[i] / denom)
            results.append(AlternativeResult(
                index=i, name=names[i], score=float(c_base * gamma[i]), base_score=c_base,
                support_weight=float(W_cov[i]), penalty_gamma=float(gamma[i]),
                active_criteria_count=int(m_active[i]),
                status=AlternativeStatus.EVALUATED,
            ))

        # Sıralama: geçerliler skora (eşitlikte kapsama oranına) göre, yetersizler en altta
        evaluated = sorted(
            [r for r in results if r.status == AlternativeStatus.EVALUATED],
            key=lambda r: (r.score, r.support_weight), reverse=True,
        )
        insufficient = [r for r in results if r.status == AlternativeStatus.INSUFFICIENT_DATA]
        for k, r in enumerate(evaluated + insufficient, start=1):
            r.rank = k

        expl = RCZExplanation(
            weights=w_vec, active_mask=active_mask, S=S, W_cov=W_cov, m_active=m_active,
            valid_gate=valid_gate, w_eff=w_eff, V=V, v_plus=v_plus, v_minus=v_minus,
            d_plus=d_plus, d_minus=d_minus, missing_cost=missing_cost, kappa=kappa, gamma=gamma,
        )
        return results, expl

    # ------------------------------------------------------------------ #
    def fit_predict(self, X, Sigma, weights, crit_types, names=None) -> List[AlternativeResult]:
        """Karar matrisini değerlendirir ve sonuçları (orijinal sırada, rank alanı dolu) döner."""
        return self.explain(X, Sigma, weights, crit_types, names)[0]


# ====================================================================== #
# Komut satırı gösterimi: python core.py
# ====================================================================== #
def run_steps_sequentially():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    alts = ["Ürün A", "Ürün B", "Ürün C", "Ürün D", "Ürün E"]
    crit_names = ["Hız (+)", "Fiyat (-)", "RAM (+)", "Pil (+)"]
    crit_types = [CritType.BENEFIT, CritType.COST, CritType.BENEFIT, CritType.BENEFIT]
    weights = np.array([0.25, 0.25, 0.25, 0.25])
    X = np.array([
        [8.0, 5000.0, 16.0, 10.0],
        [9.0, 7000.0, 0.0, 12.0],
        [6.0, 3000.0, 8.0, 0.0],
        [7.0, 4500.0, 32.0, 6.0],
        [10.0, 8000.0, 0.0, 0.0],
    ])
    Sigma = np.array([
        ["A", "A", "A", "A"],
        ["A", "A", "I", "A"],
        ["A", "A", "A", "I"],
        ["A", "A", "A", "A"],
        ["A", "A", "I", "I"],
    ])
    cfg = RCZConfig()
    results, e = RCZTOPSIS(cfg).explain(X, Sigma, weights, crit_types, names=alts)

    line = "-" * 80
    print("=" * 80)
    print("R-CZ-TOPSIS v1.1 — ADIM ADIM HESAPLAMA (global ağırlık)")
    print("=" * 80)
    print(f"Konfigürasyon: W_threshold={cfg.w_threshold}, m_min={cfg.min_active_criteria}, "
          f"alpha={cfg.alpha}, local_reweighting={cfg.local_reweighting}")
    print("\nKarar matrisi (A=ölçülmüş, I=eksik):")
    for n, row, sig in zip(alts, X, Sigma):
        print(f"  {n:<8}: " + ", ".join(f"{v:>7.1f} ({s})" for v, s in zip(row, sig)))

    print(f"\n{line}\n[1] Sütun norm paydaları S_j (yalnızca 'A' hücreleri)")
    for j, c in enumerate(crit_names):
        print(f"  {c:<10} aktif={int(e.active_mask[:, j].sum())}  S={e.S[j]:.4f}")

    print(f"\n{line}\n[2] Kapsama W_i ve Hard Gatekeeper")
    for i, n in enumerate(alts):
        print(f"  {n:<8} W={e.W_cov[i]:.2f}  m*={e.m_active[i]}  -> {'GEÇTİ' if e.valid_gate[i] else 'ELENDİ'}")

    print(f"\n{line}\n[3] Ağırlıklı normalize matris V (eksik = NaN)")
    for i, n in enumerate(alts):
        print(f"  {n:<8} " + ", ".join("  NaN " if np.isnan(v) else f"{v:.4f}" for v in e.V[i]))

    print(f"\n{line}\n[4] İdeal (v+) ve anti-ideal (v-) noktalar")
    for j, c in enumerate(crit_names):
        print(f"  {c:<10} ({crit_types[j].value:<7}) v+={e.v_plus[j]:.4f}  v-={e.v_minus[j]:.4f}")

    print(f"\n{line}\n[5] Alt-uzay mesafeleri, ceza ve skor")
    print(f"  {'Aday':<8} {'D+':>7} {'D-':>7} {'C_base':>7} {'eksikMal':>8} {'kappa':>6} {'Gamma':>7} {'C*':>7}")
    for r in sorted(results, key=lambda r: r.index):
        i = r.index
        print(f"  {r.name:<8} {e.d_plus[i]:>7.4f} {e.d_minus[i]:>7.4f} {r.base_score:>7.4f} "
              f"{e.missing_cost[i]:>8.2f} {e.kappa[i]:>6.2f} {r.penalty_gamma:>7.4f} {r.score:>7.4f}")

    print(f"\n{line}\n[6] Sıralama")
    for r in sorted(results, key=lambda r: r.rank):
        print(f"  {r.rank}. {r.name:<8} C*={r.score:.4f}  W={r.support_weight:.2f}  {r.status.value}")
    print("=" * 80)


if __name__ == "__main__":
    run_steps_sequentially()