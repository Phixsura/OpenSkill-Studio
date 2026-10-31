"""Idempotency Store — ensure exactly-once request processing.

Implements:
- Store request fingerprint + response for dedup
- TTL-based expiry for completed entries
- In-progress locking to prevent concurrent duplicates
- Response replay for duplicate requests
- Fingerprint from method + path + body hash
"""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import time


@dataclass
class IdempotencyEntry:
    key: str
    fingerprint: str
    status: str = "in_progress"  # in_progress, completed, expired
    response: dict = field(default_factory=dict)
    status_code: int = 0
    created_at: float = 0.0
    completed_at: float = 0.0
    expires_at: float = 0.0
    replay_count: int = 0


class IdempotencyStoreService:
    DEFAULT_TTL = 86400  # 24 hours
    MAX_ENTRIES = 100000

    def __init__(self):
        self._entries: dict[str, IdempotencyEntry] = {}

    def _fingerprint(self, method: str, path: str, body: str) -> str:
        content = f"{method}:{path}:{body}"
        return hashlib.sha256(content.encode()).hexdigest()[:32]

    def check(self, idempotency_key: str, method: str = "",
              path: str = "", body: str = "") -> tuple[str, dict | None]:
        """Check if request is a duplicate.
        Returns: (status, cached_response_or_None)
        - "new": first time seeing this key
        - "in_progress": another request with this key is being processed
        - "completed": already processed, returns cached response
        """
        now = time.time()
        entry = self._entries.get(idempotency_key)

        if not entry:
            return "new", None

        # Check expiry
        if entry.expires_at > 0 and now > entry.expires_at:
            del self._entries[idempotency_key]
            return "new", None

        # Verify fingerprint if provided
        if method and entry.fingerprint:
            fp = self._fingerprint(method, path, body)
            if fp != entry.fingerprint:
                return "conflict", None  # same key, different request

        if entry.status == "in_progress":
            return "in_progress", None

        if entry.status == "completed":
            entry.replay_count += 1
            return "completed", {"response": entry.response,
                                  "status_code": entry.status_code,
                                  "replayed": True,
                                  "replay_count": entry.replay_count}

        return "new", None

    def start(self, idempotency_key: str, method: str = "",
              path: str = "", body: str = "",
              ttl: int = 0) -> IdempotencyEntry:
        """Mark a request as in-progress."""
        now = time.time()
        fp = self._fingerprint(method, path, body) if method else ""
        ttl = ttl or self.DEFAULT_TTL
        entry = IdempotencyEntry(
            key=idempotency_key, fingerprint=fp,
            status="in_progress", created_at=now,
            expires_at=now + ttl)
        self._entries[idempotency_key] = entry

        # Evict oldest if over limit
        if len(self._entries) > self.MAX_ENTRIES:
            self._evict_oldest()

        return entry

    def complete(self, idempotency_key: str, response: dict,
                 status_code: int = 200) -> bool:
        """Mark request as completed with cached response."""
        entry = self._entries.get(idempotency_key)
        if not entry or entry.status != "in_progress":
            return False
        entry.status = "completed"
        entry.response = response
        entry.status_code = status_code
        entry.completed_at = time.time()
        return True

    def fail(self, idempotency_key: str) -> bool:
        """Remove in-progress entry on failure (allow retry)."""
        entry = self._entries.get(idempotency_key)
        if entry and entry.status == "in_progress":
            del self._entries[idempotency_key]
            return True
        return False

    def _evict_oldest(self) -> int:
        now = time.time()
        # First evict expired
        expired = [k for k, v in self._entries.items()
                   if v.expires_at > 0 and v.expires_at < now]
        for k in expired:
            del self._entries[k]
        if len(self._entries) <= self.MAX_ENTRIES:
            return len(expired)
        # Then evict oldest completed
        completed = sorted(
            [(k, v) for k, v in self._entries.items() if v.status == "completed"],
            key=lambda x: x[1].created_at)
        evicted = 0
        for k, _ in completed[:len(self._entries) - self.MAX_ENTRIES + 100]:
            del self._entries[k]
            evicted += 1
        return len(expired) + evicted

    def stats(self) -> dict:
        in_progress = sum(1 for e in self._entries.values() if e.status == "in_progress")
        completed = sum(1 for e in self._entries.values() if e.status == "completed")
        total_replays = sum(e.replay_count for e in self._entries.values())
        return {"total": len(self._entries), "in_progress": in_progress,
                "completed": completed, "total_replays": total_replays}
