"""API Consumer Response Cache — per-consumer response caching with TTL."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import time
import structlog

log = structlog.get_logger()

@dataclass
class CachedResponse:
    cache_key: str
    endpoint: str
    method: str
    status_code: int
    body_hash: str
    cached_at: float = field(default_factory=time.time)
    ttl_s: int = 300
    hits: int = 0

    @property
    def expired(self) -> bool:
        return time.time() > self.cached_at + self.ttl_s

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponseCache:
    def __init__(self, max_entries: int = 5000) -> None:
        self._cache: dict[tuple[str, str, str], CachedResponse] = {}
        self._max = max(100, max_entries)
        self._stats: dict[str, dict[str, int]] = {}

    def put(self, installation_id: str, consumer_id: str, endpoint: str, method: str, status_code: int, body: str, ttl_s: int = 300) -> CachedResponse:
        if not installation_id: raise ValueError("installation_id is required")
        cache_key = hashlib.sha256(f"{consumer_id}:{method}:{endpoint}".encode()).hexdigest()[:16]
        body_hash = hashlib.sha256(body.encode()).hexdigest()[:16]
        entry = CachedResponse(cache_key=cache_key, endpoint=endpoint, method=method, status_code=status_code, body_hash=body_hash, ttl_s=ttl_s)
        key = (installation_id, consumer_id, cache_key)
        self._cache[key] = entry
        return entry

    def get(self, installation_id: str, consumer_id: str, endpoint: str, method: str) -> CachedResponse | None:
        cache_key = hashlib.sha256(f"{consumer_id}:{method}:{endpoint}".encode()).hexdigest()[:16]
        key = (installation_id, consumer_id, cache_key)
        entry = self._cache.get(key)
        if entry is None: return None
        if entry.expired: del self._cache[key]; return None
        entry.hits += 1
        stats = self._stats.setdefault(installation_id, {"hits": 0, "misses": 0})
        stats["hits"] += 1
        return entry

    def invalidate(self, installation_id: str, consumer_id: str, endpoint: str, method: str) -> bool:
        cache_key = hashlib.sha256(f"{consumer_id}:{method}:{endpoint}".encode()).hexdigest()[:16]
        key = (installation_id, consumer_id, cache_key)
        if key in self._cache: del self._cache[key]; return True
        return False

    def hit_rate(self, installation_id: str) -> float:
        s = self._stats.get(installation_id, {"hits": 0, "misses": 0})
        total = s["hits"] + s["misses"]
        return round((s["hits"] / total) * 100, 1) if total > 0 else 0.0

    def cache_size(self, installation_id: str) -> int:
        return sum(1 for (inst, _, _) in self._cache if inst == installation_id)
