"""Consumer API Access Token Cache — in-memory token cache with TTL."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
import structlog

log = structlog.get_logger()

@dataclass
class CachedToken:
    token_hash: str
    consumer_id: str
    scopes: list[str]
    cached_at: datetime
    expires_at: datetime

@dataclass
class CacheStats:
    total_entries: int
    hit_count: int
    miss_count: int
    hit_rate_pct: float
    eviction_count: int

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiAccessTokenCache:
    def __init__(self, ttl_seconds: int = 300, max_entries: int = 10000) -> None:
        self._cache: dict[tuple[str, str], CachedToken] = {}
        self._ttl = ttl_seconds
        self._max = max_entries
        self._hits: dict[str, int] = {}
        self._misses: dict[str, int] = {}
        self._evictions: dict[str, int] = {}

    def put(self, installation_id: str, token_hash: str, consumer_id: str, scopes: list[str], now: datetime) -> CachedToken:
        if not installation_id:
            raise ValueError("installation_id is required")
        # Evict if full
        inst_entries = [(k, v) for k, v in self._cache.items() if k[0] == installation_id]
        if len(inst_entries) >= self._max:
            oldest = min(inst_entries, key=lambda x: x[1].cached_at)
            del self._cache[oldest[0]]
            self._evictions[installation_id] = self._evictions.get(installation_id, 0) + 1
        entry = CachedToken(token_hash=token_hash, consumer_id=consumer_id, scopes=scopes, cached_at=now, expires_at=now + timedelta(seconds=self._ttl))
        self._cache[(installation_id, token_hash)] = entry
        return entry

    def get(self, installation_id: str, token_hash: str, now: datetime) -> CachedToken | None:
        key = (installation_id, token_hash)
        entry = self._cache.get(key)
        if not entry:
            self._misses[installation_id] = self._misses.get(installation_id, 0) + 1
            return None
        if now >= entry.expires_at:
            del self._cache[key]
            self._misses[installation_id] = self._misses.get(installation_id, 0) + 1
            return None
        self._hits[installation_id] = self._hits.get(installation_id, 0) + 1
        return entry

    def invalidate(self, installation_id: str, token_hash: str) -> bool:
        key = (installation_id, token_hash)
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def get_stats(self, installation_id: str) -> CacheStats:
        entries = sum(1 for (inst, _) in self._cache if inst == installation_id)
        hits = self._hits.get(installation_id, 0)
        misses = self._misses.get(installation_id, 0)
        total = hits + misses
        rate = (hits / total * 100) if total > 0 else 0
        return CacheStats(total_entries=entries, hit_count=hits, miss_count=misses, hit_rate_pct=round(rate, 1), eviction_count=self._evictions.get(installation_id, 0))
