"""App API Webhook Idempotency — prevent duplicate webhook deliveries."""
from __future__ import annotations
import hashlib
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class IdempotencyRecord:
    key: str
    event_type: str
    destination: str
    delivered: bool = False

class AppAPIWebhookIdempotency:
    def __init__(self) -> None:
        self._records: dict[tuple[str, str], IdempotencyRecord] = {}

    def generate_key(self, event_type: str, payload: str, destination: str) -> str:
        return hashlib.sha256(f"{event_type}:{destination}:{payload}".encode()).hexdigest()[:32]

    def check_and_record(self, installation_id: str, key: str, event_type: str, destination: str) -> tuple[bool, IdempotencyRecord]:
        """Returns (is_duplicate, record)."""
        if not installation_id: raise ValueError("installation_id is required")
        k = (installation_id, key)
        if k in self._records:
            return True, self._records[k]
        r = IdempotencyRecord(key=key, event_type=event_type, destination=destination)
        self._records[k] = r
        return False, r

    def mark_delivered(self, installation_id: str, key: str) -> IdempotencyRecord:
        r = self._records.get((installation_id, key))
        if r is None: raise KeyError(f"Record {key} not found")
        r.delivered = True
        return r

    def count(self, installation_id: str) -> int:
        return sum(1 for (inst, _) in self._records if inst == installation_id)
