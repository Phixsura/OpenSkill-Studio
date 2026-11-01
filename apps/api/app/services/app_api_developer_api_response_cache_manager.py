"""App API Developer Response Cache Manager — API response caching strategies."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class CacheEntry:
    cache_key: str
    endpoint: str
    ttl_seconds: int
    created_at: float = field(default_factory=time.time)
    hit_count: int = 0
    size_bytes: int = 0

    @property
    def expired(self) -> bool:
        return time.time() > self.created_at + self.ttl_seconds

@dataclass
class CacheStats:
    total_entries: int = 0
    hits: int = 0
    misses: int = 0
    total_bytes: int = 0

    @property
    def hit_rate_pct(self) -> float:
        total = self.hits + self.misses
        return round(self.hits / total * 100, 1) if total > 0 else 0.0

class AppAPIDeveloperAPIResponseCacheManager:
    def __init__(self, max_entries: int = 1000) -> None:
        self._max = max(1, max_entries)
        self._cache: dict[tuple[str, str], CacheEntry] = {}
        self._stats: dict[str, CacheStats] = {}

    def put(self, installation_id: str, cache_key: str, endpoint: str, ttl_seconds: int, size_bytes: int = 0) -> CacheEntry:
        if not installation_id: raise ValueError("installation_id is required")
        if ttl_seconds <= 0: raise ValueError("ttl must be positive")
        key = (installation_id, cache_key)
        e = CacheEntry(cache_key=cache_key, endpoint=endpoint, ttl_seconds=ttl_seconds, size_bytes=size_bytes)
        self._cache[key] = e
        return e

    def get(self, installation_id: str, cache_key: str) -> CacheEntry | None:
        key = (installation_id, cache_key)
        e = self._cache.get(key)
        stats = self._stats.setdefault(installation_id, CacheStats())
        if e is None or e.expired:
            stats.misses += 1
            if e and e.expired: del self._cache[key]
            return None
        e.hit_count += 1
        stats.hits += 1
        return e

    def invalidate(self, installation_id: str, endpoint: str) -> int:
        keys = [(inst, ck) for (inst, ck), e in self._cache.items() if inst == installation_id and e.endpoint == endpoint]
        for k in keys: del self._cache[k]
        return len(keys)

    def stats(self, installation_id: str) -> CacheStats:
        s = self._stats.get(installation_id, CacheStats())
        s.total_entries = sum(1 for (inst, _) in self._cache if inst == installation_id)
        s.total_bytes = sum(e.size_bytes for (inst, _), e in self._cache.items() if inst == installation_id)
        return s
