"""App API Developer Webhook Event Deduplication — prevent duplicate event delivery."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import time
import structlog

log = structlog.get_logger()

@dataclass
class DeduplicationEntry:
    event_hash: str
    event_type: str
    first_seen_at: float = field(default_factory=time.time)
    seen_count: int = 1

class AppAPIDeveloperAPIApiWebhookEventDeduplication:
    def __init__(self, ttl_seconds: int = 3600, max_entries: int = 100000) -> None:
        self._ttl = ttl_seconds
        self._max = max_entries
        self._entries: dict[tuple[str, str], DeduplicationEntry] = {}

    def check(self, installation_id: str, event_type: str, payload: str) -> tuple[bool, str]:
        """Returns (is_duplicate, event_hash)."""
        if not installation_id: raise ValueError("installation_id is required")
        event_hash = hashlib.sha256(f"{event_type}:{payload}".encode()).hexdigest()[:32]
        key = (installation_id, event_hash)
        existing = self._entries.get(key)
        if existing and not self._expired(existing):
            existing.seen_count += 1
            return (True, event_hash)
        self._entries[key] = DeduplicationEntry(event_hash=event_hash, event_type=event_type)
        return (False, event_hash)

    def stats(self, installation_id: str) -> dict[str, int]:
        active = [(k, e) for k, e in self._entries.items() if k[0] == installation_id and not self._expired(e)]
        return {"active_hashes": len(active), "duplicates_caught": sum(e.seen_count - 1 for _, e in active)}

    def cleanup(self, installation_id: str) -> int:
        expired = [k for k, e in self._entries.items() if k[0] == installation_id and self._expired(e)]
        for k in expired: del self._entries[k]
        return len(expired)

    def _expired(self, entry: DeduplicationEntry) -> bool:
        return time.time() - entry.first_seen_at > self._ttl
