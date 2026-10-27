"""R-CZ-TOPSIS Sözleşme ve Şema Katmanı (Model Contract & Schema).

Yüksek güvenceli kurumsal ve askeri karar destek sistemleri için:
- Tip güvenli, doğrulanabilir girdi/çıktı veri yapıları
- Kapsamlı `DecisionDataset.validate()` metodu (fail-closed doğrulama)
- Deterministik IEEE-754 tam hassasiyetli SHA-256 veri bütünlüğü özeti
- Kriptografik denetim makbuzu (IntegrityReceipt)
"""
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
from typing import Any, Dict, List, Optional, Set
import uuid

import numpy as np

from .types import CritType, Context, AlternativeStatus, RCZConfig


class ProfileType(str, Enum):
    GENERIC = "GENERIC_RESEARCH"
    TENDER_AUDIT = "TENDER_OFFICIAL_AUDIT"
    MILITARY_ADVISORY = "MILITARY_C2_ADVISORY"


class DataClassification(str, Enum):
    UNCLASSIFIED = "UNCLASSIFIED"
    INTERNAL_SENSITIVE = "INTERNAL_SENSITIVE"
    RESTRICTED = "RESTRICTED"


class MissingReason(str, Enum):
    """Eksik verinin kök neden analizi (rastgele arıza vs. kasıtlı karartma)."""
    NOT_MISSING = "NOT_MISSING"
    SENSOR_FAULT = "SENSOR_FAULT"
    TRANSMISSION_DELAY = "TRANSMISSION_DELAY"
    JAMMING_SUSPECTED = "JAMMING_SUSPECTED"
    MAINTENANCE = "MAINTENANCE"
    UNREPORTED_VENDOR_PRICE = "UNREPORTED_VENDOR_PRICE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class CriterionDef:
    """Tek bir karar kriterinin doğrulanmış sözleşmesi."""
    name: str
    crit_type: CritType
    weight: float
    unit: str = ""
    description: str = ""
    is_critical_cost: bool = False

    def validate(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Kriter adı boş olamaz.")
        if not np.isfinite(self.weight):
            raise ValueError(f"'{self.name}' kriteri için ağırlık sonlu bir sayı olmalıdır.")
        if self.weight <= 0.0:
            raise ValueError(f"'{self.name}' kriteri için ağırlık pozitif (> 0) olmalıdır: {self.weight}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "crit_type": self.crit_type.value,
            "weight": float(self.weight),
            "unit": self.unit,
            "description": self.description,
            "is_critical_cost": bool(self.is_critical_cost),
        }


@dataclass(frozen=True)
class AlternativeDef:
    """Tek bir karar alternatifinin kimlik ve meta veri sözleşmesi."""
    id: str
    name: str
    provider: str = ""
    data_timestamp_utc: Optional[str] = None
    telemetry_age_seconds: Optional[float] = None
    classification: DataClassification = DataClassification.UNCLASSIFIED

    def validate(self) -> None:
        if not self.id or not self.id.strip():
            raise ValueError("Alternatif ID'si boş olamaz.")
        if not self.name or not self.name.strip():
            raise ValueError(f"Alternatif '{self.id}' için isim boş olamaz.")
        if self.telemetry_age_seconds is not None:
            if not np.isfinite(self.telemetry_age_seconds) or self.telemetry_age_seconds < 0.0:
                raise ValueError(f"Alternatif '{self.id}' için telemetri yaşı negatif veya tanımsız olamaz: {self.telemetry_age_seconds}")
        if self.data_timestamp_utc is not None:
            try:
                datetime.fromisoformat(self.data_timestamp_utc)
            except Exception as e:
                raise ValueError(f"Alternatif '{self.id}' için geçersiz ISO zaman damgası: {self.data_timestamp_utc}") from e

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "provider": self.provider,
            "data_timestamp_utc": self.data_timestamp_utc,
            "telemetry_age_seconds": self.telemetry_age_seconds,
            "classification": self.classification.value,
        }


@dataclass
class DecisionDataset:
    """Doğrulanmış ve bütünlüğü mühürlenmiş karar veri paketi."""
    criteria: List[CriterionDef]
    alternatives: List[AlternativeDef]
    X: np.ndarray             # (n, m) float64
    Sigma: np.ndarray         # (n, m) object ('A' veya 'I')
    missing_reasons: Dict[Any, Any] = field(default_factory=dict)
    dataset_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    model_version: str = "1.1.1"

    def get_missing_reason(self, row: int, col: int) -> MissingReason:
        if not self.missing_reasons:
            return MissingReason.UNKNOWN
        cand = self.alternatives[row]
        crit = self.criteria[col]
        for key in ((row, col), (cand.id, crit.name), f"{row}_{col}", f"{cand.id}:{crit.name}"):
            if key in self.missing_reasons:
                val = self.missing_reasons[key]
                if isinstance(val, MissingReason):
                    return val
                try:
                    return MissingReason(str(val))
                except Exception:
                    pass
        return MissingReason.UNKNOWN

    def validate(self) -> None:
        """Kapsamlı fail-closed şema doğrulaması gerçekleştirir."""
        if len(self.criteria) < 2:
            raise ValueError(f"Karar matrisinde en az 2 kriter bulunmalıdır; mevcut: {len(self.criteria)}")
        if len(self.alternatives) < 1:
            raise ValueError(f"Karar matrisinde en az 1 alternatif bulunmalıdır; mevcut: {len(self.alternatives)}")

        n_alts = len(self.alternatives)
        n_crits = len(self.criteria)

        if not isinstance(self.X, np.ndarray) or self.X.shape != (n_alts, n_crits):
            raise ValueError(f"X matris boyutu {self.X.shape if hasattr(self.X, 'shape') else type(self.X)}, beklenen: ({n_alts}, {n_crits})")
        if not isinstance(self.Sigma, np.ndarray) or self.Sigma.shape != (n_alts, n_crits):
            raise ValueError(f"Sigma matris boyutu {self.Sigma.shape if hasattr(self.Sigma, 'shape') else type(self.Sigma)}, beklenen: ({n_alts}, {n_crits})")

        # Sigma değerleri
        valid_sigma = {"A", "I", Context.ACTION.value, Context.INACTION.value}
        invalid_sig_cells = set(self.Sigma.ravel()) - valid_sigma
        if invalid_sig_cells:
            raise ValueError(f"Sigma matrisinde geçersiz hücre değerleri: {invalid_sig_cells}. Yalnızca 'A' ve 'I' kabul edilir.")

        # Kriter ve Alternatif doğrulamaları
        crit_names: Set[str] = set()
        for c in self.criteria:
            c.validate()
            if c.name in crit_names:
                raise ValueError(f"Yinelenen kriter adı tespit edildi: '{c.name}'")
            crit_names.add(c.name)

        alt_ids: Set[str] = set()
        for a in self.alternatives:
            a.validate()
            if a.id in alt_ids:
                raise ValueError(f"Yinelenen alternatif ID'si tespit edildi: '{a.id}'")
            alt_ids.add(a.id)

        # Ağırlık toplamı kontrolü
        w_sum = sum(c.weight for c in self.criteria)
        if not np.isclose(w_sum, 1.0, atol=1e-4):
            raise ValueError(f"Kriter ağırlıklarının toplamı 1.0 olmalıdır; mevcut toplam: {w_sum:.6f}")

        # Aktif hücre doğrulaması
        active_mask = (self.Sigma == "A") | (self.Sigma == Context.ACTION.value)
        if np.any(~np.isfinite(self.X[active_mask])):
            raise ValueError("Aktif ('A') işaretli veri hücrelerinde NaN veya sonsuz (inf) değer bulunamaz.")

        # Her kriterde en az bir aktif ölçüm bulunmalı
        col_active_counts = active_mask.sum(axis=0)
        if np.any(col_active_counts == 0):
            empty_cols = [self.criteria[j].name for j in range(n_crits) if col_active_counts[j] == 0]
            raise ValueError(f"Şu kriterlerde hiçbir aktif ('A') ölçüm bulunamadı: {empty_cols}")

    def compute_sha256(self) -> str:
        """Kayıpsız IEEE-754 ve kanonik sıralı JSON üzerinden tam hassasiyetli SHA-256 üretir."""
        self.validate()

        # IEEE-754 binary64 değerini round-trip edebilen ondalık gösterim.
        # 15 basamak bazı birbirinden farklı float değerlerini aynı hash'e
        # indirger; 17 anlamlı basamak bu sınıf için güvenli sınırdır.
        exact_matrix_x = [[f"{float(val):.17e}" for val in row] for row in self.X]
        exact_matrix_sig = [[str(cell) for cell in row] for row in self.Sigma]

        canonical_dict = {
            "dataset_id": str(self.dataset_id),
            "created_at_utc": str(self.created_at_utc),
            "model_version": str(self.model_version),
            "criteria": [c.to_dict() for c in self.criteria],
            "alternatives": [a.to_dict() for a in self.alternatives],
            "exact_matrix_X": exact_matrix_x,
            "matrix_Sigma": exact_matrix_sig,
        }
        if self.missing_reasons:
            canonical_dict["missing_reasons"] = {
                str(k): (v.value if isinstance(v, MissingReason) else str(v))
                for k, v in sorted(self.missing_reasons.items(), key=lambda item: str(item[0]))
            }
        encoded = json.dumps(canonical_dict, sort_keys=True, ensure_ascii=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class IntegrityReceipt:
    """Hesaplamanın değiştirilemez denetim makbuzu."""
    run_id: str
    timestamp_utc: str
    profile: ProfileType
    dataset_hash: str
    config_hash: str
    output_hash: str
    combined_receipt_hash: str
    operator_id: str
    compliance_notice: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "timestamp_utc": self.timestamp_utc,
            "profile": self.profile.value,
            "dataset_hash": self.dataset_hash,
            "config_hash": self.config_hash,
            "output_hash": self.output_hash,
            "combined_receipt_hash": self.combined_receipt_hash,
            "operator_id": self.operator_id,
            "compliance_notice": self.compliance_notice,
        }


def hash_config(cfg: RCZConfig) -> str:
    """Motor konfigürasyonunun deterministik SHA-256 özetini üretir."""
    cfg_data = {
        "alpha": f"{float(cfg.alpha):.17e}",
        "w_threshold": f"{float(cfg.w_threshold):.17e}",
        "min_active_criteria": int(cfg.min_active_criteria),
        "eps": f"{float(cfg.eps):.17e}",
        "local_reweighting": bool(cfg.local_reweighting),
        "threshold_tol": f"{float(cfg.threshold_tol):.17e}",
    }
    encoded = json.dumps(cfg_data, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
