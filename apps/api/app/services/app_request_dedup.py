"""App Request Dedup — deduplicate incoming requests by content hash.

Prevents duplicate request processing:
- Hash-based deduplication
- TTL-based window for dedup detection
- Track duplicate counts
- Per-installation scoped dedup
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class DedupResult:
    """Result of a dedup check."""

    is_duplicate: bool
    content_hash: str
    first_seen_at: float = 0.0
    duplicate_count: int = 0


class AppRequestDedup:
    """Deduplicate incoming requests by content hash."""

    def __init__(self, ttl_seconds: float = 300) -> None:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be > 0")
        self._ttl = ttl_seconds
        # (installation_id, hash) → (first_seen, count)
        self._seen: dict[tuple[str, str], tuple[float, int]] = {}

    def check(
        self,
        installation_id: str,
        method: str,
        path: str,
        body: str = "",
        now: float | None = None,
    ) -> DedupResult:
        """Check if a request is a duplicate."""
        if not installation_id:
            raise ValueError("installation_id is required")

        now = now or time.time()
        content = f"{method.upper()}:{path}:{body}"
        h = hashlib.sha256(content.encode()).hexdigest()[:16]
        key = (installation_id, h)

        entry = self._seen.get(key)
        if entry:
            first_seen, count = entry
            if now - first_seen < self._ttl:
                self._seen[key] = (first_seen, count + 1)
                return DedupResult(
                    is_duplicate=True, content_hash=h,
                    first_seen_at=first_seen, duplicate_count=count + 1,
                )
            # Expired — treat as new
            del self._seen[key]

        self._seen[key] = (now, 0)
        return DedupResult(is_duplicate=False, content_hash=h, first_seen_at=now)

    def cleanup_expired(self, now: float | None = None) -> int:
        now = now or time.time()
        expired = [k for k, (ts, _) in self._seen.items() if now - ts >= self._ttl]
        for k in expired:
            del self._seen[k]
        return len(expired)

    def stats(self, installation_id: str) -> dict:
        entries = [(ts, cnt) for (inst, _), (ts, cnt) in self._seen.items() if inst == installation_id]
        total_dupes = sum(cnt for _, cnt in entries)
        return {"tracked": len(entries), "total_duplicates": total_dupes}
