"""API Endpoint Cache Invalidator — manage cache invalidation for API responses."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import time
import structlog

log = structlog.get_logger()

@dataclass
class CacheEntry:
    cache_key: str
    endpoint: str
    method: str
    etag: str = ""
    cached_at: float = field(default_factory=time.time)
    ttl_s: int = 300
    hit_count: int = 0

    @property
    def expired(self) -> bool:
        return time.time() > self.cached_at + self.ttl_s

@dataclass
class InvalidationEvent:
    event_id: str
    pattern: str  # endpoint pattern to invalidate
    reason: str
    invalidated_count: int = 0
    timestamp: float = field(default_factory=time.time)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointCacheInvalidator:
    def __init__(self) -> None:
        self._cache: dict[tuple[str, str], CacheEntry] = {}
        self._events: dict[str, list[InvalidationEvent]] = {}

    def cache_response(self, installation_id: str, endpoint: str, method: str, ttl_s: int = 300) -> CacheEntry:
        if not installation_id: raise ValueError("installation_id is required")
        cache_key = hashlib.sha256(f"{method}:{endpoint}".encode()).hexdigest()[:12]
        entry = CacheEntry(cache_key=cache_key, endpoint=endpoint, method=method, ttl_s=ttl_s, etag=f'W/"{cache_key}"')
        self._cache[(installation_id, cache_key)] = entry
        return entry

    def check_cache(self, installation_id: str, method: str, endpoint: str) -> CacheEntry | None:
        for (inst, _), entry in self._cache.items():
            if inst == installation_id and entry.method == method and entry.endpoint == endpoint:
                if entry.expired:
                    return None
                entry.hit_count += 1
                return entry
        return None

    def invalidate(self, installation_id: str, pattern: str, reason: str = "") -> InvalidationEvent:
        count = 0
        keys_to_remove = []
        for (inst, key), entry in self._cache.items():
            if inst == installation_id and (pattern == "*" or pattern in entry.endpoint):
                keys_to_remove.append((inst, key))
                count += 1
        for k in keys_to_remove: del self._cache[k]
        event = InvalidationEvent(event_id=f"inv-{int(time.time())}", pattern=pattern, reason=reason, invalidated_count=count)
        self._events.setdefault(installation_id, []).append(event)
        return event

    def cache_stats(self, installation_id: str) -> dict[str, int]:
        entries = [(k, e) for k, e in self._cache.items() if k[0] == installation_id]
        total_hits = sum(e.hit_count for _, e in entries)
        return {"cached_entries": len(entries), "total_hits": total_hits}

    def recent_invalidations(self, installation_id: str, limit: int = 10) -> list[InvalidationEvent]:
        return list(reversed(self._events.get(installation_id, [])[-limit:]))
