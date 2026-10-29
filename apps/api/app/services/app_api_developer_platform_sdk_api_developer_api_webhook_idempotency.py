"""App API Developer Webhook Idempotency — ensure at-most-once delivery."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import time
import structlog

log = structlog.get_logger()

@dataclass
class IdempotencyRecord:
    idempotency_key: str
    event_hash: str
    destination: str
    delivered_at: float = field(default_factory=time.time)
    ttl_seconds: int = 86400

    @property
    def expired(self) -> bool:
        return time.time() > self.delivered_at + self.ttl_seconds

class AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookIdempotency:
    def __init__(self, default_ttl: int = 86400) -> None:
        self._ttl = default_ttl
        self._records: dict[tuple[str, str, str], IdempotencyRecord] = {}

    def check_and_store(self, installation_id: str, destination: str, idempotency_key: str, event_payload: str) -> tuple[bool, IdempotencyRecord]:
        """Returns (is_duplicate, record)."""
        if not installation_id: raise ValueError("installation_id is required")
        if not idempotency_key: raise ValueError("idempotency_key is required")
        event_hash = hashlib.sha256(event_payload.encode()).hexdigest()[:32]
        key = (installation_id, destination, idempotency_key)
        existing = self._records.get(key)
        if existing and not existing.expired:
            if existing.event_hash != event_hash:
                raise ValueError("Payload mismatch for idempotency key")
            return (True, existing)
        r = IdempotencyRecord(idempotency_key=idempotency_key, event_hash=event_hash, destination=destination, ttl_seconds=self._ttl)
        self._records[key] = r
        return (False, r)

    def is_duplicate(self, installation_id: str, destination: str, idempotency_key: str) -> bool:
        key = (installation_id, destination, idempotency_key)
        r = self._records.get(key)
        return r is not None and not r.expired

    def cleanup(self, installation_id: str) -> int:
        expired = [k for k, r in self._records.items() if k[0] == installation_id and r.expired]
        for k in expired: del self._records[k]
        return len(expired)

    def active_count(self, installation_id: str) -> int:
        return sum(1 for k, r in self._records.items() if k[0] == installation_id and not r.expired)
