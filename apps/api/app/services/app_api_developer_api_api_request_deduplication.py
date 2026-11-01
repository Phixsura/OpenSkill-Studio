"""App API Developer API Request Deduplication — idempotent request handling."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import time
import structlog

log = structlog.get_logger()

@dataclass
class DeduplicationEntry:
    idempotency_key: str
    payload_hash: str
    status_code: int
    created_at: float = field(default_factory=time.time)
    hit_count: int = 0

class AppAPIDeveloperAPIApiRequestDeduplication:
    def __init__(self, ttl_seconds: int = 86400) -> None:
        self._ttl = ttl_seconds
        self._entries: dict[tuple[str, str], DeduplicationEntry] = {}

    def check_or_store(self, installation_id: str, idempotency_key: str, payload: str, status_code: int) -> tuple[bool, DeduplicationEntry]:
        """Returns (is_duplicate, entry). If duplicate, entry has the original response."""
        if not installation_id: raise ValueError("installation_id is required")
        if not idempotency_key: raise ValueError("idempotency_key is required")
        key = (installation_id, idempotency_key)
        payload_hash = hashlib.sha256(payload.encode()).hexdigest()[:16]
        existing = self._entries.get(key)
        if existing and not self._expired(existing):
            if existing.payload_hash != payload_hash:
                raise ValueError("Payload mismatch for idempotency key")
            existing.hit_count += 1
            return (True, existing)
        entry = DeduplicationEntry(idempotency_key=idempotency_key, payload_hash=payload_hash, status_code=status_code)
        self._entries[key] = entry
        return (False, entry)

    def stats(self, installation_id: str) -> dict[str, int]:
        entries = [(k, e) for k, e in self._entries.items() if k[0] == installation_id and not self._expired(e)]
        total = len(entries)
        duplicates = sum(e.hit_count for _, e in entries)
        return {"active_keys": total, "duplicate_hits": duplicates}

    def cleanup(self, installation_id: str) -> int:
        expired = [k for k, e in self._entries.items() if k[0] == installation_id and self._expired(e)]
        for k in expired: del self._entries[k]
        return len(expired)

    def _expired(self, entry: DeduplicationEntry) -> bool:
        return time.time() - entry.created_at > self._ttl
