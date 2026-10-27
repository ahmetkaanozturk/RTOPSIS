from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Context(str, Enum):
    """Gözlem bağlamı (Context)."""
    ACTION = "A"      # Aktif gözlem / Gerçek ölçüm
    INACTION = "I"    # Eylemsizlik / Bilgi yokluğu / Boş hücre


class CritType(str, Enum):
    """Kriter optimizasyon yönü."""
    BENEFIT = "benefit"  # Fayda (En büyük en iyi)
    COST = "cost"        # Maliyet (En küçük en iyi)


class AlternativeStatus(str, Enum):
    """Alternatif değerlendirme durumu."""
    EVALUATED = "EVALUATED"                      # Başarıyla değerlendirildi
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"      # Bilgi eşiği yetersiz, elendi


@dataclass(frozen=True)
class RCZConfig:
    """R-CZ-TOPSIS hiper-parametre konfigürasyonu."""
    w_threshold: float = 0.50          # Asgari toplam ağırlık eşiği (W_threshold)
    min_active_criteria: int = 2       # Asgari bilinmesi gereken kriter adedi
    alpha: float = 0.50                # Riskten kaçınma katsayısı
    eps: float = 1e-12                 # Sıfıra bölünme koruma payı
    # v1.1 (denetim sonrası): Varsayılan olarak GLOBAL ağırlıklar kullanılır.
    # True yapılırsa formülasyon v1.0'daki w'_ij = w_j / W_i yerel ağırlıklandırması
    # kullanılır. Bu seçenek, eksik veriyi ödüllendiren sapma nedeniyle (bkz.
    # matematiksel_formulasyon.md, Revizyon Notu) yalnızca karşılaştırma amaçlı tutulmuştur.
    local_reweighting: bool = False
    # Ondalık toplamlar için eşik toleransı (örn. 0.1+0.2+0.2 = 0.49999999...)
    threshold_tol: float = 1e-9


@dataclass
class AlternativeResult:
    """Bir alternatifin hesaplama ve sıralama çıktısı."""
    index: int
    name: str
    score: float                       # Nihai performans indeksi (C*)
    base_score: float                  # Ceza öncesi temel skor (C_base)
    support_weight: float              # Bilgi kapsama oranı (W_i)
    penalty_gamma: float               # Epistemik güvenilirlik çarpanı (Gamma_i)
    active_criteria_count: int         # Aktif kriter adedi (m_i*)
    status: AlternativeStatus          # Değerlendirme statüsü
    rank: Optional[int] = None         # Sıralama (1 = En iyi)


@dataclass
class RCZExplanation:
    """Hesaplamanın tüm ara adımları (şeffaflık / raporlama için)."""
    weights: object            # Normalize global ağırlıklar (m,)
    active_mask: object        # (n, m) bool
    S: object                  # Sütun norm paydaları (m,)
    W_cov: object              # Bilgi kapsama oranı (n,)
    m_active: object           # Aktif kriter sayısı (n,)
    valid_gate: object         # Gatekeeper sonucu (n,)
    w_eff: object              # Kullanılan ağırlıklar (n, m)
    V: object                  # Ağırlıklı normalize matris, eksik = NaN (n, m)
    v_plus: object             # (m,)
    v_minus: object            # (m,)
    d_plus: object             # (n,) geçersizler için NaN
    d_minus: object            # (n,)
    missing_cost: object       # (n,)
    kappa: object              # (n,)
    gamma: object              # (n,)