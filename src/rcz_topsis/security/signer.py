"""R-CZ-TOPSIS Dijital İmza ve Makbuz Doğrulama Katmanı (Digital Signatures).

Yüksek güvence standartları:
- Her karar makbuzu (IntegrityReceipt) kurumsal anahtarla dijital olarak imzalanır.
- Salt SHA-256 hash'i yerine yetkili kurum imzasını taşır.
- İnternetsiz (air-gapped) ortamlarda harici bağımlılık gerektirmeden çalışır.
- İmza bozulması, parametre manipülasyonu veya sahte makbuz durumlarını doğrular.
"""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib
import hmac
import json
import secrets
from typing import Any, Dict, Optional

from ..schema import IntegrityReceipt


@dataclass(frozen=True)
class SignedReceipt:
    """Kurumsal anahtarla imzalanmış karar makbuzu sözleşmesi."""
    receipt: IntegrityReceipt
    signature_algorithm: str
    key_id: str
    signature_hex: str
    signed_at_utc: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "receipt": self.receipt.to_dict(),
            "signature_algorithm": self.signature_algorithm,
            "key_id": self.key_id,
            "signature_hex": self.signature_hex,
            "signed_at_utc": self.signed_at_utc,
        }


class ReceiptSigner:
    """Karar makbuzlarını imzalayan ve imza bütünlüğünü doğrulayan servis."""

    def __init__(self, key_id: str = "KURUM-MOHUR-2026-V1", secret_key: Optional[bytes] = None):
        self.key_id = key_id
        self._secret = secret_key or secrets.token_bytes(32)

    def sign(self, receipt: IntegrityReceipt) -> SignedReceipt:
        """Makbuzun birleşik hash'ini ve içeriğini kurumsal anahtarla imzalar."""
        now_ts = datetime.now(timezone.utc).isoformat()
        canonical_payload = (
            f"{receipt.run_id}|{receipt.profile.value}|{receipt.dataset_hash}|"
            f"{receipt.config_hash}|{receipt.output_hash}|{receipt.combined_receipt_hash}|{now_ts}"
        )
        sig = hmac.new(self._secret, canonical_payload.encode("utf-8"), hashlib.sha256).hexdigest()

        return SignedReceipt(
            receipt=receipt,
            signature_algorithm="HMAC-SHA256",
            key_id=self.key_id,
            signature_hex=sig,
            signed_at_utc=now_ts,
        )

    def verify(self, signed_receipt: SignedReceipt) -> bool:
        """İmzalı makbuzun geçerli ve tahrif edilmemiş olduğunu doğrular."""
        if signed_receipt.key_id != self.key_id:
            return False

        r = signed_receipt.receipt
        canonical_payload = (
            f"{r.run_id}|{r.profile.value}|{r.dataset_hash}|"
            f"{r.config_hash}|{r.output_hash}|{r.combined_receipt_hash}|{signed_receipt.signed_at_utc}"
        )
        expected_sig = hmac.new(self._secret, canonical_payload.encode("utf-8"), hashlib.sha256).hexdigest()
        return hmac.compare_digest(signed_receipt.signature_hex, expected_sig)
