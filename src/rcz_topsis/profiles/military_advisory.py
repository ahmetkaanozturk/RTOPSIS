"""R-CZ-TOPSIS Askeri Taktik Karar Destek Ürün Profili (Human-in-the-Loop Advisory).

TEMEL OPERASYONEL SINIRLAR VE GÜVENCELER:
1. KESİN OTONOMİ KISITI (NON-AUTONOMOUS CONSTRAINT):
   Sistem hiçbir koşulda otonom angajman, silah tahsisi veya ateşleme emri üretemez.
   Yalnızca görevli taktik harekât subayına açıklanabilir karar gerekçesi ve öncelik sıralaması sunar.
2. TELEMETRİ TAZELİĞİ VE SENSÖR YAŞI (DATA FRESHNESS):
   Sensör verisi belirli bir eşiğin (ör. 10-30 sn) üzerinde gecikmişse iz "STALE / BAYAT TELEMETRİ"
   olarak işaretlenir ve operatör onayına zorlanır.
3. ELEKTRONİK HARP & KARARTMA DİRENCİ (GRACEFUL DEGRADATION):
   Jammer veya radar karartması altında yalnızca aktif kalan optik/termal kanallarda
   alt-uzay mesafe hesaplaması sürdürülür.
4. GÜVENLİ DURUŞ (FAIL-CLOSED SAFETY):
   Veri kalitesi asgari barajın altındaysa hedef "YETERSİZ VERİ - BEKLEMEDE" statüsüne alınır;
   şüpheli temaslara körlemesine otomatik hedefleme yapılması engellenir.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, List, Optional
import uuid

import numpy as np

from ..core import RCZTOPSIS
from ..types import AlternativeStatus, CritType, RCZConfig
from ..schema import (
    CriterionDef,
    AlternativeDef,
    DecisionDataset,
    IntegrityReceipt,
    ProfileType,
    MissingReason,
    hash_config,
)
from ..audit import AuditHashChain


AUTONOMOUS_ENGAGEMENT_ALLOWED: bool = False


@dataclass
class TacticalTrackAdvisory:
    """Tek bir taktik izin (hedef / hava unsuru) operatör danışma kartı."""
    track_id: str
    target_designation: str
    priority_rank: int
    threat_score: float
    information_coverage: float
    telemetry_age_seconds: Optional[float]
    freshness_status: str              # Örn: GUNCEL, GECIKMELI_BAYAT, KARARTILMIS_ALT_UZAY
    operational_advisory: str
    requires_visual_confirmation: bool
    fail_closed_hold: bool             # Veri yetersizliği veya aşırı bayatlık nedeniyle beklemede mi?


@dataclass
class MilitaryAdvisoryResult:
    """Taktik C2 karar destek çıktısı."""
    mission_id: str
    timestamp_utc: str
    operator_id: str
    top_priority_track: Optional[TacticalTrackAdvisory]
    track_advisories: List[TacticalTrackAdvisory]
    active_jamming_detected: bool
    stale_telemetry_detected: bool
    audit_receipt: IntegrityReceipt
    operational_status: str = "ENGAGEMENT_ADVISORY_READY"
    doctrine_notice: str = (
        "DOKTRİN VE GÜVENLİK UYARISI: Bu prototip yalnızca karar destek danışmanı (Advisory Engine) "
        "olarak görev yapar. Her türlü angajman, silah tahsisi veya müdahale kararı "
        "YALNIZCA YETKİLİ İNSAN HAREKÂT SUBAYININ (Human-in-the-Loop) sorumluluğu ve onayındadır. "
        "Bu yazılım NATO veya herhangi bir milli doktrin için uygunluk/sertifikasyon belgesi değildir."
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "timestamp_utc": self.timestamp_utc,
            "operator_id": self.operator_id,
            "top_priority_track": self.top_priority_track.__dict__ if self.top_priority_track else None,
            "track_advisories": [t.__dict__ for t in self.track_advisories],
            "active_jamming_detected": self.active_jamming_detected,
            "stale_telemetry_detected": self.stale_telemetry_detected,
            "operational_status": self.operational_status,
            "audit_receipt": self.audit_receipt.to_dict(),
            "doctrine_notice": self.doctrine_notice,
            "autonomous_engagement_allowed": AUTONOMOUS_ENGAGEMENT_ALLOWED,
        }


class MilitaryAdvisoryProfile:
    """Askeri taktik karar destek profili yöneticisi."""

    def __init__(self, audit_chain: Optional[AuditHashChain] = None):
        self.audit_chain = audit_chain or AuditHashChain()

    def evaluate(
        self,
        dataset: DecisionDataset,
        operator_id: str,
        mission_id: str = "MISSION-DEFAULT",
        max_freshness_seconds: float = 15.0,
        config: Optional[RCZConfig] = None,
    ) -> MilitaryAdvisoryResult:
        if not operator_id.strip():
            raise ValueError("Askeri karar destek profilinde yetkili Operatör/Subay kimliği zorunludur.")

        # KESİN GÜVENLİK İNVARYANTI
        if AUTONOMOUS_ENGAGEMENT_ALLOWED:
            raise RuntimeError("GÜVENLİK İHLALİ: Otonom angajman bayrağı kesinlikle aktif edilemez.")

        cfg = config or RCZConfig(alpha=0.5, w_threshold=0.50, min_active_criteria=2)
        eval_id = str(uuid.uuid4())
        now_ts = datetime.now(timezone.utc).isoformat()

        # 1. Denetim kaydı başlat
        self.audit_chain.record_event(
            event_type="TACTICAL_ADVISORY_REQUESTED",
            operator_id=operator_id,
            profile=ProfileType.MILITARY_ADVISORY.value,
            details={
                "mission_id": mission_id,
                "dataset_id": dataset.dataset_id,
                "max_freshness_seconds": max_freshness_seconds,
            },
        )

        weights = [c.weight for c in dataset.criteria]
        types = [c.crit_type for c in dataset.criteria]
        names = [a.name for a in dataset.alternatives]

        # 2. Karar motoru çalıştırma
        engine = RCZTOPSIS(cfg)
        raw_results = engine.fit_predict(
            X=dataset.X,
            Sigma=dataset.Sigma,
            weights=weights,
            crit_types=types,
            names=names,
        )

        # 3. Taktik iz danışma kartları
        advisories: List[TacticalTrackAdvisory] = []
        jamming_detected = False
        stale_detected = False

        has_explicit_reasons = bool(getattr(dataset, "missing_reasons", None))

        for r in raw_results:
            cand = dataset.alternatives[r.index]
            age = cand.telemetry_age_seconds

            # Tazelik kontrolü
            is_stale = (age is not None and age > max_freshness_seconds)
            is_critically_stale = (age is not None and age > (2.0 * max_freshness_seconds))
            if is_stale:
                stale_detected = True

            # Karartma & kök neden kontrolü
            inactive_count = sum(1 for j in range(len(dataset.criteria)) if dataset.Sigma[r.index, j] in ("I", "0_I"))
            track_jamming = False
            for j in range(len(dataset.criteria)):
                if dataset.Sigma[r.index, j] in ("I", "0_I"):
                    reason = dataset.get_missing_reason(r.index, j) if hasattr(dataset, "get_missing_reason") else MissingReason.UNKNOWN
                    if reason == MissingReason.JAMMING_SUSPECTED:
                        track_jamming = True
                    elif not has_explicit_reasons:
                        # Kök neden sözlüğü verilmemişse geriye dönük uyumluluk gereği her eksiklik potansiyel karartma sayılır
                        track_jamming = True

            if track_jamming:
                jamming_detected = True

            # Durum metni ve operasyonel öneri
            if r.status == AlternativeStatus.INSUFFICIENT_DATA:
                fresh_str = "BILGI_YETERSIZ_KARARTMA"
                adv_text = "Hedef veri kapsama oranı asgari eşiğin altında. Düşman karartması veya sensör kaybı şüphesi. Körlemesine angajman engellendi."
                req_visual = True
                fail_hold = True
            elif is_critically_stale:
                fresh_str = f"KRITIK_BAYAT_TELEMETRI ({age:.1f}sn)"
                adv_text = f"Sensör izi kritik bayatlık sınırını ({2.0 * max_freshness_seconds:.1f}sn) aştı. Hedef izi donduruldu, angajman engellendi."
                req_visual = True
                fail_hold = True
            elif is_stale:
                fresh_str = f"BAYAT_TELEMETRI ({age:.1f}sn)"
                adv_text = f"Sensör izi {age:.1f} saniye öncesine ait. Dinamik manevra olasılığı nedeniyle pozisyon doğrulaması gereklidir."
                req_visual = True
                fail_hold = False
            elif inactive_count > 0:
                fresh_str = f"KISMI_KARARTMA ({inactive_count} Kriter Eksik)"
                adv_text = "Elektronik harp/karartma altında sağlam kalan optik/termal sensörlerin alt-uzayında önceliklendirildi. Temkin cezası uygulandı."
                req_visual = True
                fail_hold = False
            else:
                fresh_str = "GUNCEL_TAM_TELEMETRI"
                adv_text = "Tüm radar/ESM/optik sensör verileri günceldir. Tehdit katsayısı doğrulanmış durumdadır."
                req_visual = False
                fail_hold = False

            advisories.append(TacticalTrackAdvisory(
                track_id=cand.id,
                target_designation=cand.name,
                priority_rank=r.rank,
                threat_score=float(r.score),
                information_coverage=float(r.support_weight),
                telemetry_age_seconds=age,
                freshness_status=fresh_str,
                operational_advisory=adv_text,
                requires_visual_confirmation=req_visual,
                fail_closed_hold=fail_hold,
            ))

        advisories.sort(key=lambda x: (x.priority_rank if x.priority_rank > 0 else 9999))
        
        # Güvenli Duruş (Fail-Closed Invariant): Yalnızca beklemede OLMAYAN hedefler angajman önerisine çıkabilir
        actionable_tracks = [a for a in advisories if a.priority_rank > 0 and not a.fail_closed_hold]
        if actionable_tracks:
            top_advisory = actionable_tracks[0]
            op_status = "ENGAGEMENT_ADVISORY_READY"
        else:
            top_advisory = None
            op_status = "HOLD_NO_ACTIONABLE_TRACKS"

        # 4. Kriptografik Denetim Makbuzu
        ds_hash = dataset.compute_sha256()
        cfg_hash = hash_config(cfg)
        out_bytes = json.dumps([a.__dict__ for a in advisories], sort_keys=True).encode("utf-8")
        out_hash = hashlib.sha256(out_bytes).hexdigest()
        comb_hash = hashlib.sha256(f"{eval_id}|{ds_hash}|{cfg_hash}|{out_hash}".encode("utf-8")).hexdigest()

        receipt = IntegrityReceipt(
            run_id=eval_id,
            timestamp_utc=now_ts,
            profile=ProfileType.MILITARY_ADVISORY,
            dataset_hash=ds_hash,
            config_hash=cfg_hash,
            output_hash=out_hash,
            combined_receipt_hash=comb_hash,
            operator_id=operator_id,
            compliance_notice="Askeri Karar Destek Danışmanı (İnsan Onayına Tabi, Otonom Müdahale Yetkisiz)",
        )

        # 5. Denetim zincirine tamamlanma kaydı
        self.audit_chain.record_event(
            event_type="TACTICAL_ADVISORY_DELIVERED",
            operator_id=operator_id,
            profile=ProfileType.MILITARY_ADVISORY.value,
            details={
                "eval_id": eval_id,
                "top_target": top_advisory.target_designation if top_advisory else "YOK (HOLD)",
                "operational_status": op_status,
                "receipt_hash": comb_hash,
                "jamming_detected": jamming_detected,
                "stale_telemetry": stale_detected,
            },
        )

        return MilitaryAdvisoryResult(
            mission_id=mission_id,
            timestamp_utc=now_ts,
            operator_id=operator_id,
            top_priority_track=top_advisory,
            track_advisories=advisories,
            active_jamming_detected=jamming_detected,
            stale_telemetry_detected=stale_detected,
            audit_receipt=receipt,
            operational_status=op_status,
        )
