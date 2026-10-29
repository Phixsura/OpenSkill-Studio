"""App API Response Cache — cache API responses with TTL.

Manages response caching:
- Cache responses by key
- TTL-based expiration
- Hit/miss tracking
- Per-installation scoped caches
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class CachedResponse:
    """A cached API response."""

    cache_key: str
    status_code: int
    body: str
    cached_at: float = field(default_factory=time.time)
    ttl_seconds: int = 300
    hits: int = 0

    @property
    def is_expired(self) -> bool:
        return (time.time() - self.cached_at) > self.ttl_seconds


class AppAPIResponseCache:
    """Cache API responses with TTL."""

    def __init__(self, max_entries: int = 1000) -> None:
        self._max = max(1, max_entries)
        self._cache: dict[tuple[str, str], CachedResponse] = {}
        self._hits: int = 0
        self._misses: int = 0

    def put(
        self, installation_id: str, cache_key: str,
        status_code: int, body: str, ttl_seconds: int = 300,
    ) -> CachedResponse:
        if not installation_id:
            raise ValueError("installation_id is required")

        entry = CachedResponse(
            cache_key=cache_key, status_code=status_code,
            body=body, ttl_seconds=ttl_seconds,
        )
        self._cache[(installation_id, cache_key)] = entry
        return entry

    def get(self, installation_id: str, cache_key: str) -> CachedResponse | None:
        key = (installation_id, cache_key)
        entry = self._cache.get(key)
        if entry is None:
            self._misses += 1
            return None
        if entry.is_expired:
            del self._cache[key]
            self._misses += 1
            return None
        entry.hits += 1
        self._hits += 1
        return entry

    def invalidate(self, installation_id: str, cache_key: str) -> bool:
        key = (installation_id, cache_key)
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def hit_rate(self) -> float:
        total = self._hits + self._misses
        if total == 0:
            return 0.0
        return round(self._hits / total * 100, 1)

    def size(self, installation_id: str) -> int:
        return sum(1 for (inst, _) in self._cache if inst == installation_id)
