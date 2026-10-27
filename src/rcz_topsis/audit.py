"""R-CZ-TOPSIS Denetim Zinciri (Tamper-Evident Audit Log & Hash Chain).

Kurumsal denetim süreçlerine hazırlık amacıyla:
- Her hesaplama ve operatör eylemini kriptografik hash zincirine bağlar.
- Olayların sonradan silinmesi, değiştirilmesi veya sırasının bozulması durumunda
  bütünlük ihlalini matematiksel olarak yakalar.
- Harici disk veya dosya sistemine taşınabilir JSON audit izi ihraç eder.
"""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


GENESIS_HASH = "0" * 64


@dataclass(frozen=True)
class AuditRecord:
    sequence: int
    timestamp_utc: str
    event_type: str
    operator_id: str
    profile: str
    payload_hash: str
    prev_hash: str
    record_hash: str
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AuditHashChain:
    """Tek yönlü kriptografik hash zinciri ile çalışan denetim kaydı yöneticisi."""

    def __init__(self, initial_records: Optional[List[AuditRecord]] = None):
        self._records: List[AuditRecord] = []
        if initial_records:
            for r in initial_records:
                self._records.append(r)

    @property
    def latest_hash(self) -> str:
        return self._records[-1].record_hash if self._records else GENESIS_HASH

    @property
    def records(self) -> List[AuditRecord]:
        return list(self._records)

    def record_event(
        self,
        event_type: str,
        operator_id: str,
        profile: str,
        details: Dict[str, Any],
    ) -> AuditRecord:
        """Yeni bir denetim olayını zincirin sonuna ekler ve hash'ler."""
        seq = len(self._records) + 1
        ts = datetime.now(timezone.utc).isoformat()
        prev = self.latest_hash

        # Payload hash
        details_json = json.dumps(details, sort_keys=True, ensure_ascii=True, default=str)
        payload_hash = hashlib.sha256(details_json.encode("utf-8")).hexdigest()

        # Block record hash
        header = f"{seq}|{ts}|{event_type}|{operator_id}|{profile}|{payload_hash}|{prev}"
        record_hash = hashlib.sha256(header.encode("utf-8")).hexdigest()

        record = AuditRecord(
            sequence=seq,
            timestamp_utc=ts,
            event_type=event_type,
            operator_id=operator_id,
            profile=profile,
            payload_hash=payload_hash,
            prev_hash=prev,
            record_hash=record_hash,
            details=details,
        )
        self._records.append(record)
        return record

    def verify_integrity(self) -> bool:
        """Tüm zincirin bütünlüğünü ve sıra bağlarını doğrular."""
        if not self._records:
            return True

        expected_prev = GENESIS_HASH
        for idx, rec in enumerate(self._records, start=1):
            if rec.sequence != idx:
                return False
            if rec.prev_hash != expected_prev:
                return False

            # Hash doğrulaması
            details_json = json.dumps(rec.details, sort_keys=True, ensure_ascii=True, default=str)
            payload_hash = hashlib.sha256(details_json.encode("utf-8")).hexdigest()
            if payload_hash != rec.payload_hash:
                return False

            header = f"{rec.sequence}|{rec.timestamp_utc}|{rec.event_type}|{rec.operator_id}|{rec.profile}|{payload_hash}|{rec.prev_hash}"
            computed_hash = hashlib.sha256(header.encode("utf-8")).hexdigest()
            if computed_hash != rec.record_hash:
                return False

            expected_prev = rec.record_hash

        return True

    def export_json(self, output_path: Path) -> None:
        """Denetim zincirini doğrulanabilir JSON dosyası olarak diske kaydeder."""
        data = {
            "chain_length": len(self._records),
            "latest_hash": self.latest_hash,
            "is_valid": self.verify_integrity(),
            "exported_at_utc": datetime.now(timezone.utc).isoformat(),
            "records": [r.to_dict() for r in self._records],
        }
        output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


class PersistentAuditStore:
    """Diske append-only JSONL formatında yazan ve başlatmada bütünlük doğrulayan kalıcı denetim deposu."""

    def __init__(self, log_path: Path):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._chain = AuditHashChain()
        self._load_and_verify()

    def _load_and_verify(self) -> None:
        if not self.log_path.exists():
            return
        records = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    rec = AuditRecord(
                        sequence=data["sequence"],
                        timestamp_utc=data["timestamp_utc"],
                        event_type=data["event_type"],
                        operator_id=data["operator_id"],
                        profile=data["profile"],
                        payload_hash=data["payload_hash"],
                        prev_hash=data["prev_hash"],
                        record_hash=data["record_hash"],
                        details=data["details"],
                    )
                    records.append(rec)
                except Exception as e:
                    raise IOError(f"Denetim günlüğü bozuk (Satır {line_no}): {e}") from e

        self._chain = AuditHashChain(records)
        if not self._chain.verify_integrity():
            raise ValueError(f"Denetim günlüğü bütünlük ihlali! Dosya tahrif edilmiş olabilir: {self.log_path}")

    @property
    def latest_hash(self) -> str:
        return self._chain.latest_hash

    @property
    def records(self) -> List[AuditRecord]:
        return self._chain.records

    def record_event(
        self,
        event_type: str,
        operator_id: str,
        profile: str,
        details: Dict[str, Any],
    ) -> AuditRecord:
        record = self._chain.record_event(
            event_type=event_type,
            operator_id=operator_id,
            profile=profile,
            details=details,
        )
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
            f.flush()
        return record

    def verify_disk_integrity(self) -> bool:
        if not self.log_path.exists():
            return True
        try:
            records = []
            with open(self.log_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    rec = AuditRecord(
                        sequence=data["sequence"],
                        timestamp_utc=data["timestamp_utc"],
                        event_type=data["event_type"],
                        operator_id=data["operator_id"],
                        profile=data["profile"],
                        payload_hash=data["payload_hash"],
                        prev_hash=data["prev_hash"],
                        record_hash=data["record_hash"],
                        details=data["details"],
                    )
                    records.append(rec)
            temp_chain = AuditHashChain(records)
            return temp_chain.verify_integrity()
        except Exception:
            return False

