"""API Consumer Webhook Idempotency — ensure webhook deliveries are idempotent."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import time
import structlog

log = structlog.get_logger()

@dataclass
class IdempotencyRecord:
    idempotency_key: str
    event_id: str
    consumer_id: str
    delivered: bool = True
    first_delivery_at: float = field(default_factory=time.time)
    delivery_count: int = 1

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookIdempotency:
    def __init__(self, retention_hours: int = 24) -> None:
        self._records: dict[tuple[str, str], IdempotencyRecord] = {}
        self._retention_s = max(3600, retention_hours * 3600)
        self._stats: dict[str, dict[str, int]] = {}

    def check_and_record(self, installation_id: str, consumer_id: str, event_id: str, payload_hash: str = "") -> tuple[bool, IdempotencyRecord]:
        """Returns (is_new, record). If is_new=False, delivery was already made."""
        if not installation_id: raise ValueError("installation_id is required")
        idem_key = hashlib.sha256(f"{consumer_id}:{event_id}:{payload_hash}".encode()).hexdigest()[:20]
        key = (installation_id, idem_key)
        existing = self._records.get(key)
        stats = self._stats.setdefault(installation_id, {"new": 0, "duplicate": 0})
        if existing:
            now = time.time()
            if (now - existing.first_delivery_at) < self._retention_s:
                existing.delivery_count += 1
                stats["duplicate"] += 1
                return False, existing
        record = IdempotencyRecord(idempotency_key=idem_key, event_id=event_id, consumer_id=consumer_id)
        self._records[key] = record
        stats["new"] += 1
        return True, record

    def duplicate_rate(self, installation_id: str) -> float:
        s = self._stats.get(installation_id, {"new": 0, "duplicate": 0})
        total = s["new"] + s["duplicate"]
        if total == 0: return 0.0
        return round((s["duplicate"] / total) * 100, 1)

    def stats(self, installation_id: str) -> dict[str, int]:
        return self._stats.get(installation_id, {"new": 0, "duplicate": 0})

    def record_count(self, installation_id: str) -> int:
        return sum(1 for (inst, _) in self._records if inst == installation_id)
