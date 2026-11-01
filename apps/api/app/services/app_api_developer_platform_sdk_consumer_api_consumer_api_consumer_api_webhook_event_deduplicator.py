"""Consumer API Webhook Event Deduplicator — prevent duplicate webhook event deliveries."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import structlog

log = structlog.get_logger()

@dataclass
class DeduplicationResult:
    is_duplicate: bool
    event_fingerprint: str
    original_event_id: str | None = None

class AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiWebhookEventDeduplicator:
    def __init__(self, ttl_hours: int = 24, max_entries: int = 100000) -> None:
        self._seen: dict[tuple[str, str, str], tuple[str, datetime]] = {}  # (inst, consumer, fingerprint) -> (event_id, seen_at)
        self._ttl_hours = ttl_hours
        self._max = max_entries

    @staticmethod
    def compute_fingerprint(event_type: str, payload_json: str) -> str:
        return hashlib.sha256(f"{event_type}:{payload_json}".encode()).hexdigest()[:24]

    def check_and_record(self, installation_id: str, consumer_id: str, event_id: str, event_type: str, payload_json: str, now: datetime) -> DeduplicationResult:
        if not installation_id:
            raise ValueError("installation_id is required")
        fp = self.compute_fingerprint(event_type, payload_json)
        key = (installation_id, consumer_id, fp)
        existing = self._seen.get(key)
        if existing:
            orig_id, seen_at = existing
            if now < seen_at + timedelta(hours=self._ttl_hours):
                return DeduplicationResult(is_duplicate=True, event_fingerprint=fp, original_event_id=orig_id)
        # Evict oldest if over limit
        inst_entries = [(k, v) for k, v in self._seen.items() if k[0] == installation_id]
        if len(inst_entries) >= self._max:
            oldest = min(inst_entries, key=lambda x: x[1][1])
            del self._seen[oldest[0]]
        self._seen[key] = (event_id, now)
        return DeduplicationResult(is_duplicate=False, event_fingerprint=fp)

    def cleanup(self, installation_id: str, now: datetime) -> int:
        cutoff = now - timedelta(hours=self._ttl_hours)
        expired = [k for k, (_, seen_at) in self._seen.items() if k[0] == installation_id and seen_at < cutoff]
        for k in expired:
            del self._seen[k]
        return len(expired)

    def stats(self, installation_id: str) -> dict[str, int]:
        count = sum(1 for (inst, _, _) in self._seen if inst == installation_id)
        return {"tracked_fingerprints": count}
