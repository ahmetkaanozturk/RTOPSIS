"""R-CZ-TOPSIS Uygulama Servis Katmanı (Application Service Layer).

Bu servis, sunucu/çekirdek mimarisinde arayüz (dashboard/CLI/API) ile motor arasındaki
bağlantıyı kurar. İş kuralları, oturum yönetimi, RBAC yetkilendirme, kalıcı denetim
zinciri ve kurumsal kriptografik mühürleme bu katman üzerinden yönetilir.
"""
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .core import RCZTOPSIS
from .types import RCZConfig
from .schema import (
    DecisionDataset,
    ProfileType,
    IntegrityReceipt,
)
from .audit import PersistentAuditStore, AuditRecord
from .security.auth import (
    AuthenticationManager,
    UserSession,
    TwoPersonAuthorization,
    Role,
    Permission,
)
from .security.signer import ReceiptSigner, SignedReceipt
from .profiles.tender import TenderProfile, TenderEvaluationResult, TenderCommissionAuth
from .profiles.military_advisory import MilitaryAdvisoryProfile, MilitaryAdvisoryResult


class DecisionService:
    """Yüksek güvenceli karar destek servis koordinatörü."""

    def __init__(
        self,
        audit_log_path: Optional[Path] = None,
        auth_manager: Optional[AuthenticationManager] = None,
        signer: Optional[ReceiptSigner] = None,
    ):
        log_path = audit_log_path or Path("data/audit/audit_trail.jsonl")
        self.audit_store = PersistentAuditStore(log_path)
        self.auth_manager = auth_manager or AuthenticationManager()
        self.signer = signer or ReceiptSigner()

        # Profil yöneticilerini kalıcı denetim deposuyla senkronize başlat
        self._tender_profile = TenderProfile(audit_chain=self.audit_store._chain)
        self._military_profile = MilitaryAdvisoryProfile(audit_chain=self.audit_store._chain)

    def authenticate(self, user_id: str) -> UserSession:
        """Kullanıcı kimliğini doğrular ve güvenli oturum üretir."""
        session = self.auth_manager.authenticate(user_id)
        self.audit_store.record_event(
            event_type="USER_AUTHENTICATED",
            operator_id=session.user_id,
            profile="SECURITY_AUTH",
            details={"role": session.role.value, "display_name": session.display_name},
        )
        return session

    def create_dual_authorization(
        self,
        tender_id: str,
        chair_session: UserSession,
        auditor_session: UserSession,
    ) -> TwoPersonAuthorization:
        """İhale için iki kişili komisyon onayını doğrular ve üretir."""
        dual_auth = TwoPersonAuthorization.create(
            auth_mgr=self.auth_manager,
            tender_id=tender_id,
            chair_session=chair_session,
            auditor_session=auditor_session,
        )
        self.audit_store.record_event(
            event_type="DUAL_AUTHORIZATION_ISSUED",
            operator_id=chair_session.user_id,
            profile=ProfileType.TENDER_AUDIT.value,
            details={
                "tender_id": tender_id,
                "auditor_id": auditor_session.user_id,
                "token_prefix": dual_auth.authorization_token[:16],
            },
        )
        return dual_auth

    def evaluate_tender(
        self,
        session: UserSession,
        dataset: DecisionDataset,
        auth: Any,
        config: Optional[RCZConfig] = None,
    ) -> Tuple[TenderEvaluationResult, SignedReceipt]:
        """Yetkilendirilmiş resmi ihale değerlendirmesini çalıştırır ve dijital olarak imzalar."""
        if not self.auth_manager.verify_session(session):
            raise PermissionError("Geçersiz veya süresi dolmuş oturum.")
        if not session.has_permission(Permission.RUN_TENDER_EVALUATION):
            raise PermissionError(f"Bu eylem için yetkiniz yok. Gerekli yetki: {Permission.RUN_TENDER_EVALUATION.value}")

        dataset.validate()
        result = self._tender_profile.evaluate(dataset=dataset, auth=auth, config=config)
        signed_receipt = self.signer.sign(result.audit_receipt)

        return result, signed_receipt

    def evaluate_military_advisory(
        self,
        session: UserSession,
        dataset: DecisionDataset,
        mission_id: str = "MISSION-DEFAULT",
        max_freshness_seconds: float = 15.0,
        config: Optional[RCZConfig] = None,
    ) -> Tuple[MilitaryAdvisoryResult, SignedReceipt]:
        """Taktik karar destek danışmanlığını çalıştırır ve dijital olarak imzalar."""
        if not self.auth_manager.verify_session(session):
            raise PermissionError("Geçersiz veya süresi dolmuş oturum.")
        if not session.has_permission(Permission.RUN_TACTICAL_ADVISORY):
            raise PermissionError(f"Bu eylem için yetkiniz yok. Gerekli yetki: {Permission.RUN_TACTICAL_ADVISORY.value}")

        dataset.validate()
        result = self._military_profile.evaluate(
            dataset=dataset,
            operator_id=session.user_id,
            mission_id=mission_id,
            max_freshness_seconds=max_freshness_seconds,
            config=config,
        )
        signed_receipt = self.signer.sign(result.audit_receipt)

        return result, signed_receipt

    def verify_audit_integrity(self) -> bool:
        """Kalıcı denetim günlüğünün disk üzerindeki bütünlüğünü doğrular."""
        return self.audit_store.verify_disk_integrity()

    def verify_signed_receipt(self, signed_receipt: SignedReceipt) -> bool:
        """Dijital imzalı karar makbuzunun geçerliliğini doğrular."""
        return self.signer.verify(signed_receipt)
