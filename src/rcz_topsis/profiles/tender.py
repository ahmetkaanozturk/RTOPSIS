"""R-CZ-TOPSIS Resmi İhale & Tedarikçi Değerlendirme Ürün Profili.

Yasal ve İdari İlkeler:
1. İnsan Karar Verici Üstünlüğü: Sistem nihai ihale kararı vermez; komisyona gerekçeli tavsiye sunar.
2. İki Kişili Onay (Two-Person Commission Rule): İhale başkanı ve denetçi onayı olmadan resmi rapor üretilmez.
3. Maliyet Şeffaflığı & İnceleme: Maliyet/fiyat kriterini bildirmeyen teklifler için otomatik "Komisyon Savunma/İnceleme" bayrağı açılır.
4. Yakın Skor Eşitlik Prosedürü: İlk iki teklif arasındaki puan farkı <= %2.0 ise komisyona zorunlu inceleme tutanağı maddesi oluşturulur.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, List, Optional
import uuid

import numpy as np

from ..core import RCZTOPSIS, RCZExplanation
from ..types import AlternativeStatus, CritType, RCZConfig
from ..schema import (
    CriterionDef,
    AlternativeDef,
    DecisionDataset,
    IntegrityReceipt,
    ProfileType,
    hash_config,
)
from ..audit import AuditHashChain


@dataclass(frozen=True)
class TenderCommissionAuth:
    """İhale komisyonu yetkilendirme ve iki kişili onay sözleşmesi."""
    tender_id: str
    commission_chair_id: str
    auditor_id: str
    approval_timestamp_utc: str
    session_notes: str = ""

    def validate(self) -> None:
        if not self.tender_id.strip():
            raise ValueError("Geçerli bir ihale ID'si zorunludur.")
        if not self.commission_chair_id.strip():
            raise ValueError("İhale Komisyon Başkanı kimliği zorunludur.")
        if not self.auditor_id.strip():
            raise ValueError("Yetkili Denetçi/Mali Üye kimliği zorunludur.")
        if self.commission_chair_id.strip() == self.auditor_id.strip():
            raise ValueError("İki kişili onay ilkesi gereği Komisyon Başkanı ve Denetçi farklı kişiler olmalıdır.")


@dataclass
class TenderCandidateReport:
    """Aday bazında ihale inceleme özeti."""
    candidate_id: str
    name: str
    rank: int
    rcz_score: float
    coverage_ratio: float
    compliance_status: str       # Örn: TAVSIYE_EDILEN, EK_INCELEME_GEREKLI, ELENDI
    missing_cost_criteria: List[str]
    has_cost_hiding_risk: bool
    commission_recommendation: str


@dataclass
class TenderEvaluationResult:
    """Resmi ihale değerlendirme sonuç paketi."""
    tender_id: str
    evaluation_id: str
    timestamp_utc: str
    top_recommendation: Optional[TenderCandidateReport]
    candidate_reports: List[TenderCandidateReport]
    requires_commission_inquiry: bool
    close_score_alert: bool
    audit_receipt: IntegrityReceipt
    commission_auth: TenderCommissionAuth
    disclaimer: str = (
        "YASAL UYARI: Bu rapor 4734 Sayılı Kamu İhale Kanunu ve ilgili tedarik mevzuatı kapsamında "
        "yalnızca İhale Komisyonu'nun takdir ve değerlendirmesine sunulan teknik bir karar destek tavsiyesidir. "
        "Yazılım tek başına nihai yüklenici belirleme yetkisine sahip değildir; nihai karar komisyon üyelerinin ıslak imzalı tutanağı ile kesinleşir."
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tender_id": self.tender_id,
            "evaluation_id": self.evaluation_id,
            "timestamp_utc": self.timestamp_utc,
            "top_recommendation": self.top_recommendation.__dict__ if self.top_recommendation else None,
            "candidate_reports": [r.__dict__ for r in self.candidate_reports],
            "requires_commission_inquiry": self.requires_commission_inquiry,
            "close_score_alert": self.close_score_alert,
            "audit_receipt": self.audit_receipt.to_dict(),
            "commission_auth": self.commission_auth.__dict__,
            "disclaimer": self.disclaimer,
        }


class TenderProfile:
    """Resmi ihale ve tedarikçi değerlendirme profili uygulayıcısı."""

    def __init__(self, audit_chain: Optional[AuditHashChain] = None):
        self.audit_chain = audit_chain or AuditHashChain()

    def evaluate(
        self,
        dataset: DecisionDataset,
        auth: Any,
        config: Optional[RCZConfig] = None,
    ) -> TenderEvaluationResult:
        if hasattr(auth, "chair_session") and hasattr(auth, "auditor_session"):
            chair_id = auth.chair_session.user_id
            auditor_id = auth.auditor_session.user_id
            tender_id = auth.tender_id
            commission_auth = TenderCommissionAuth(
                tender_id=tender_id,
                commission_chair_id=chair_id,
                auditor_id=auditor_id,
                approval_timestamp_utc=auth.created_at_utc,
                session_notes=f"HMAC-Token: {auth.authorization_token[:16]}...",
            )
        else:
            auth.validate()
            chair_id = auth.commission_chair_id
            auditor_id = auth.auditor_id
            tender_id = auth.tender_id
            commission_auth = auth

        cfg = config or RCZConfig(alpha=0.5, w_threshold=0.50, min_active_criteria=2)
        eval_id = str(uuid.uuid4())
        now_ts = datetime.now(timezone.utc).isoformat()

        # 1. Denetim zincirine oturum başlangıcını kaydet
        self.audit_chain.record_event(
            event_type="TENDER_EVALUATION_INITIATED",
            operator_id=chair_id,
            profile=ProfileType.TENDER_AUDIT.value,
            details={
                "tender_id": tender_id,
                "auditor_id": auditor_id,
                "eval_id": eval_id,
                "dataset_id": dataset.dataset_id,
            },
        )

        # 2. Çekirdek motor hesaplaması
        weights = [c.weight for c in dataset.criteria]
        types = [c.crit_type for c in dataset.criteria]
        names = [a.name for a in dataset.alternatives]

        engine = RCZTOPSIS(cfg)
        raw_results = engine.fit_predict(
            X=dataset.X,
            Sigma=dataset.Sigma,
            weights=weights,
            crit_types=types,
            names=names,
        )

        # 3. İhale bazında aday raporlarını derleme
        n_crits = len(dataset.criteria)
        cand_reports: List[TenderCandidateReport] = []
        requires_inquiry = False

        has_explicit_critical_def = any(c.crit_type == CritType.COST and c.is_critical_cost for c in dataset.criteria)

        for r in raw_results:
            cand_def = dataset.alternatives[r.index]
            
            # Eksik maliyet kriterlerini kritik ve ikincil olarak ayır
            missing_critical_costs = []
            missing_secondary_costs = []
            for j in range(n_crits):
                crit = dataset.criteria[j]
                if dataset.Sigma[r.index, j] in ("I", "0_I") and crit.crit_type == CritType.COST:
                    if crit.is_critical_cost:
                        missing_critical_costs.append(crit.name)
                    else:
                        missing_secondary_costs.append(crit.name)

            if not has_explicit_critical_def and missing_secondary_costs:
                missing_critical_costs.extend(missing_secondary_costs)
                missing_secondary_costs.clear()

            has_critical_risk = len(missing_critical_costs) > 0
            has_secondary_risk = len(missing_secondary_costs) > 0

            if has_critical_risk:
                requires_inquiry = True

            # Durum ve tavsiye belirleme
            if r.status == AlternativeStatus.INSUFFICIENT_DATA:
                status_str = "ELENDI_BILGI_YETERSIZ"
                comm_note = "Aday asgari teknik bilgi eşiğini (%50) sağlayamadığı için ihale şartnamesi uyarınca elenmiştir."
            elif has_critical_risk:
                status_str = "KOMISYON_SAVUNMA_TALEBI_GEREKLI"
                comm_note = f"Aday kritik teklif/fiyat kriterini ({', '.join(missing_critical_costs)}) beyan etmemiştir. İhale mevzuatı uyarınca adaya yazılı savunma süresi verilmelidir."
            elif has_secondary_risk:
                status_str = "IKINCIL_MALIYET_EKSIK_IKAZ"
                comm_note = f"Aday ikincil maliyet bileşenlerini ({', '.join(missing_secondary_costs)}) beyan etmemiştir; temkin cezası uygulanmış fakat teklif askıya alınmamıştır."
            else:
                status_str = "UYGUN_TEKLIF_TAVSIYESI"
                comm_note = "Tüm teklif bileşenleri eksiksizdir; adayın puanı resmi sıralamaya uygundur."

            all_missing_costs = missing_critical_costs + missing_secondary_costs
            cand_reports.append(TenderCandidateReport(
                candidate_id=cand_def.id,
                name=cand_def.name,
                rank=r.rank,
                rcz_score=float(r.score),
                coverage_ratio=float(r.support_weight),
                compliance_status=status_str,
                missing_cost_criteria=all_missing_costs,
                has_cost_hiding_risk=has_critical_risk,
                commission_recommendation=comm_note,
            ))

        cand_reports.sort(key=lambda x: (x.rank if x.rank > 0 else 9999))

        # 4. Yakın skor alarmı kontrolü
        close_score = False
        valid_evaluated = [c for c in cand_reports if c.rank > 0]
        if len(valid_evaluated) >= 2:
            if abs(valid_evaluated[0].rcz_score - valid_evaluated[1].rcz_score) <= 0.02:
                close_score = True

        top_rec = valid_evaluated[0] if valid_evaluated else None

        # 5. Kriptografik Denetim Makbuzu
        ds_hash = dataset.compute_sha256()
        cfg_hash = hash_config(cfg)
        out_bytes = json.dumps([c.__dict__ for c in cand_reports], sort_keys=True).encode("utf-8")
        out_hash = hashlib.sha256(out_bytes).hexdigest()
        comb_hash = hashlib.sha256(f"{eval_id}|{ds_hash}|{cfg_hash}|{out_hash}".encode("utf-8")).hexdigest()

        receipt = IntegrityReceipt(
            run_id=eval_id,
            timestamp_utc=now_ts,
            profile=ProfileType.TENDER_AUDIT,
            dataset_hash=ds_hash,
            config_hash=cfg_hash,
            output_hash=out_hash,
            combined_receipt_hash=comb_hash,
            operator_id=f"{chair_id} + {auditor_id}",
            compliance_notice="Kamu ihale süreçleri için teknik karar destek çıktısı; 4734/KİK uygunluk veya hukuki geçerlilik belgesi değildir (insan onayına tabi).",
        )

        # 6. Denetim zincirine tamamlanma kaydı
        self.audit_chain.record_event(
            event_type="TENDER_EVALUATION_COMPLETED",
            operator_id=chair_id,
            profile=ProfileType.TENDER_AUDIT.value,
            details={
                "eval_id": eval_id,
                "winner_name": top_rec.name if top_rec else "YOK",
                "receipt_hash": comb_hash,
                "close_score": close_score,
                "requires_inquiry": requires_inquiry,
            },
        )

        return TenderEvaluationResult(
            tender_id=tender_id,
            evaluation_id=eval_id,
            timestamp_utc=now_ts,
            top_recommendation=top_rec,
            candidate_reports=cand_reports,
            requires_commission_inquiry=requires_inquiry,
            close_score_alert=close_score,
            audit_receipt=receipt,
            commission_auth=commission_auth,
        )
