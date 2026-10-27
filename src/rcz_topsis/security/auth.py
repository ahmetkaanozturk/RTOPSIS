"""R-CZ-TOPSIS Rol Tabanlı Erişim Kontrolü (RBAC) ve İki Kişili Onay Katmanı.

Yüksek güvence gereksinimleri:
1. Rol Tabanlı Yetkilendirme (Role-Based Access Control - RBAC)
2. İhale ve Askeri profil ayrımının sunucu taraflı zorlanması
3. İki Kişili Komisyon Onayı (Two-Person Rule):
   - Komisyon Başkanı ve Mali Denetçi rolleri birbirinden kesin olarak ayrılır.
   - Her iki oturum kriptografik yetki jetonuyla (HMAC token) imzalanır.
   - Aynı kullanıcının iki rolü birden üstlenmesi engellenir.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import hashlib
import hmac
import json
import secrets
from typing import Any, Dict, List, Optional, Set


class Role(str, Enum):
    ANALYST = "ANALYST"                          # Genel analiz ve araştırma
    COMMISSION_CHAIR = "COMMISSION_CHAIR"        # İhale komisyon başkanı
    AUDITOR = "AUDITOR"                          # Mali/bağımsız denetçi
    TACTICAL_OFFICER = "TACTICAL_OFFICER"        # Askeri harekât subayı
    SYSTEM_ADMIN = "SYSTEM_ADMIN"                # Sistem yöneticisi


class Permission(str, Enum):
    RUN_GENERIC_EVALUATION = "RUN_GENERIC_EVALUATION"
    RUN_TENDER_EVALUATION = "RUN_TENDER_EVALUATION"
    RUN_TACTICAL_ADVISORY = "RUN_TACTICAL_ADVISORY"
    APPROVE_TENDER_AWARD = "APPROVE_TENDER_AWARD"
    EXPORT_AUDIT_LOGS = "EXPORT_AUDIT_LOGS"
    CONFIGURE_SECURITY = "CONFIGURE_SECURITY"


ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.ANALYST: {
        Permission.RUN_GENERIC_EVALUATION,
    },
    Role.COMMISSION_CHAIR: {
        Permission.RUN_GENERIC_EVALUATION,
        Permission.RUN_TENDER_EVALUATION,
        Permission.APPROVE_TENDER_AWARD,
    },
    Role.AUDITOR: {
        Permission.RUN_GENERIC_EVALUATION,
        Permission.RUN_TENDER_EVALUATION,
        Permission.APPROVE_TENDER_AWARD,
        Permission.EXPORT_AUDIT_LOGS,
    },
    Role.TACTICAL_OFFICER: {
        Permission.RUN_GENERIC_EVALUATION,
        Permission.RUN_TACTICAL_ADVISORY,
    },
    Role.SYSTEM_ADMIN: {
        Permission.RUN_GENERIC_EVALUATION,
        Permission.EXPORT_AUDIT_LOGS,
        Permission.CONFIGURE_SECURITY,
    },
}


@dataclass(frozen=True)
class UserSession:
    """Doğrulanmış kullanıcı oturumu sözleşmesi."""
    user_id: str
    display_name: str
    role: Role
    session_id: str
    issued_at_utc: str
    expires_at_utc: str
    session_hmac: str

    def is_expired(self) -> bool:
        exp = datetime.fromisoformat(self.expires_at_utc)
        return datetime.now(timezone.utc) > exp

    def has_permission(self, perm: Permission) -> bool:
        return perm in ROLE_PERMISSIONS.get(self.role, set())


class AuthenticationManager:
    """Kullanıcı kimlik doğrulama ve kriptografik oturum yöneticisi."""

    def __init__(self, server_secret: Optional[str] = None):
        self._secret = (server_secret or secrets.token_hex(32)).encode("utf-8")
        # Önceden kayıtlı kurumsal kullanıcılar (On-premise demo tablosu)
        self._users: Dict[str, Dict[str, Any]] = {
            "baskan_01": {
                "display_name": "Dr. Ahmet Yılmaz (İhale Komisyon Başkanı)",
                "role": Role.COMMISSION_CHAIR,
            },
            "denetci_01": {
                "display_name": "Mehmet Kaya (Sayıştay / Mali Denetçi)",
                "role": Role.AUDITOR,
            },
            "subay_01": {
                "display_name": "Yzb. Selim Demir (Taktik Harekât Subayı)",
                "role": Role.TACTICAL_OFFICER,
            },
            "analist_01": {
                "display_name": "Ayşe Çelik (Veri & Karar Analisti)",
                "role": Role.ANALYST,
            },
            "admin_01": {
                "display_name": "Sistem Güvenlik Yöneticisi",
                "role": Role.SYSTEM_ADMIN,
            },
        }

    def authenticate(self, user_id: str, session_ttl_minutes: int = 60) -> UserSession:
        """Kullanıcıyı doğrular ve kriptografik HMAC ile imzalanmış oturum jetonu üretir."""
        clean_id = user_id.strip().lower()
        if clean_id not in self._users:
            raise PermissionError(f"Geçersiz kullanıcı kimliği: '{user_id}'. Yetkili personel listesinde bulunamadı.")

        u = self._users[clean_id]
        now = datetime.now(timezone.utc)
        exp = now + timedelta(minutes=session_ttl_minutes)
        sid = secrets.token_hex(16)

        msg = f"{clean_id}|{u['role'].value}|{sid}|{now.isoformat()}|{exp.isoformat()}"
        sig = hmac.new(self._secret, msg.encode("utf-8"), hashlib.sha256).hexdigest()

        return UserSession(
            user_id=clean_id,
            display_name=u["display_name"],
            role=u["role"],
            session_id=sid,
            issued_at_utc=now.isoformat(),
            expires_at_utc=exp.isoformat(),
            session_hmac=sig,
        )

    def verify_session(self, session: UserSession) -> bool:
        """Oturum jetonunun bütünlüğünü ve süresini doğrular."""
        if session.is_expired():
            return False
        msg = f"{session.user_id}|{session.role.value}|{session.session_id}|{session.issued_at_utc}|{session.expires_at_utc}"
        expected_sig = hmac.new(self._secret, msg.encode("utf-8"), hashlib.sha256).hexdigest()
        return hmac.compare_digest(session.session_hmac, expected_sig)


@dataclass(frozen=True)
class TwoPersonAuthorization:
    """Kriptografik olarak doğrulanmış iki kişili onay paketi."""
    tender_id: str
    chair_session: UserSession
    auditor_session: UserSession
    authorization_token: str
    created_at_utc: str

    @classmethod
    def create(
        cls,
        auth_mgr: AuthenticationManager,
        tender_id: str,
        chair_session: UserSession,
        auditor_session: UserSession,
    ) -> "TwoPersonAuthorization":
        if not auth_mgr.verify_session(chair_session):
            raise PermissionError("Komisyon Başkanı oturum jetonu geçersiz veya süresi dolmuş.")
        if not auth_mgr.verify_session(auditor_session):
            raise PermissionError("Mali Denetçi oturum jetonu geçersiz veya süresi dolmuş.")

        if chair_session.role != Role.COMMISSION_CHAIR:
            raise PermissionError(f"Komisyon Başkanı rolü zorunludur. Alınan rol: {chair_session.role.value}")
        if auditor_session.role != Role.AUDITOR:
            raise PermissionError(f"Mali Denetçi rolü zorunludur. Alınan rol: {auditor_session.role.value}")

        if chair_session.user_id == auditor_session.user_id:
            raise PermissionError("İki kişili onay kuralı ihlali: Komisyon Başkanı ve Denetçi aynı kişi olamaz.")

        now_ts = datetime.now(timezone.utc).isoformat()
        token_msg = f"TENDER_DUAL_AUTH|{tender_id}|{chair_session.user_id}|{auditor_session.user_id}|{now_ts}"
        token = hmac.new(auth_mgr._secret, token_msg.encode("utf-8"), hashlib.sha256).hexdigest()

        return cls(
            tender_id=tender_id,
            chair_session=chair_session,
            auditor_session=auditor_session,
            authorization_token=token,
            created_at_utc=now_ts,
        )
