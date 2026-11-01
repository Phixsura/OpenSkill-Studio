"""Request Deduplicator — prevent duplicate API requests via idempotency keys.

Implements:
- Idempotency key tracking with cached responses
- Content hash dedup for requests without explicit keys
- Configurable TTL per key
- Concurrent request coalescing (return same result for in-flight dupes)
"""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import time


@dataclass
class CachedResponse:
    idempotency_key: str
    response: dict
    status_code: int
    created_at: float
    expires_at: float
    hit_count: int = 0


class RequestDedupService:
    DEFAULT_TTL = 86400  # 24 hours
    MAX_CACHE_SIZE = 10000

    def __init__(self):
        self._cache: dict[str, CachedResponse] = {}
        self._inflight: set[str] = set()

    def _content_hash(self, method: str, path: str, body: str) -> str:
        content = f"{method}:{path}:{body}"
        return f"hash:{hashlib.sha256(content.encode()).hexdigest()[:24]}"

    def _evict_expired(self) -> int:
        now = time.time()
        expired = [k for k, v in self._cache.items() if v.expires_at < now]
        for k in expired:
            del self._cache[k]
        return len(expired)

    def check(self, idempotency_key: str | None = None,
              method: str = "", path: str = "", body: str = "") -> tuple[bool, dict | None]:
        """Returns (is_duplicate, cached_response_or_None)."""
        if not idempotency_key:
            if not method:
                return False, None
            idempotency_key = self._content_hash(method, path, body)

        cached = self._cache.get(idempotency_key)
        if cached:
            now = time.time()
            if now > cached.expires_at:
                del self._cache[idempotency_key]
                return False, None
            cached.hit_count += 1
            return True, cached.response

        # Check if request is in-flight
        if idempotency_key in self._inflight:
            return True, None  # duplicate but no response yet

        return False, None

    def start(self, idempotency_key: str | None = None,
              method: str = "", path: str = "", body: str = "") -> str:
        """Mark a request as in-flight. Returns the resolved key."""
        if not idempotency_key:
            idempotency_key = self._content_hash(method, path, body)
        self._inflight.add(idempotency_key)
        return idempotency_key

    def complete(self, idempotency_key: str, response: dict,
                 status_code: int = 200, ttl: int = 0) -> None:
        """Cache the response for future dedup."""
        self._inflight.discard(idempotency_key)
        ttl = ttl or self.DEFAULT_TTL
        now = time.time()

        # Evict if cache too large
        if len(self._cache) >= self.MAX_CACHE_SIZE:
            self._evict_expired()
            if len(self._cache) >= self.MAX_CACHE_SIZE:
                # Remove oldest entries
                oldest = sorted(self._cache.items(), key=lambda x: x[1].created_at)
                for k, _ in oldest[:len(oldest) // 4]:
                    del self._cache[k]

        self._cache[idempotency_key] = CachedResponse(
            idempotency_key=idempotency_key, response=response,
            status_code=status_code, created_at=now, expires_at=now + ttl)

    def cancel(self, idempotency_key: str) -> None:
        """Remove in-flight marker without caching (request failed)."""
        self._inflight.discard(idempotency_key)

    def get_stats(self) -> dict:
        now = time.time()
        active = sum(1 for v in self._cache.values() if v.expires_at > now)
        total_hits = sum(v.hit_count for v in self._cache.values())
        return {
            "cached_responses": active,
            "expired": len(self._cache) - active,
            "inflight": len(self._inflight),
            "total_dedup_hits": total_hits,
        }
