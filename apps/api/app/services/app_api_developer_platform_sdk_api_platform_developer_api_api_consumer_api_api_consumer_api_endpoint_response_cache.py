"""Endpoint Response Cache — cache API responses with configurable TTL per endpoint."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import structlog

log = structlog.get_logger()

@dataclass
class CacheEntry:
    cache_key: str
    response_body: str
    status_code: int
    headers: dict[str, str] = field(default_factory=dict)
    created_at: datetime | None = None
    expires_at: datetime | None = None
    hit_count: int = 0

@dataclass
class CacheConfig:
    endpoint_path: str
    ttl_seconds: int = 60
    vary_by: list[str] = field(default_factory=list)  # headers to vary cache by
    max_entries: int = 1000

@dataclass
class CacheLookup:
    hit: bool
    entry: CacheEntry | None = None

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointResponseCache:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], CacheConfig] = {}
        self._entries: dict[tuple[str, str], dict[str, CacheEntry]] = {}  # (inst, path) -> {key: entry}

    def configure(self, installation_id: str, config: CacheConfig) -> CacheConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if config.ttl_seconds < 1:
            raise ValueError("ttl_seconds must be positive")
        self._configs[(installation_id, config.endpoint_path)] = config
        return config

    def _make_key(self, installation_id: str, path: str, method: str, vary_values: dict[str, str]) -> str:
        parts = [installation_id, method.upper(), path]
        config = self._configs.get((installation_id, path))
        if config:
            for h in sorted(config.vary_by):
                parts.append(f"{h}={vary_values.get(h, '')}")
        return hashlib.sha256(":".join(parts).encode()).hexdigest()[:20]

    def get(self, installation_id: str, path: str, method: str, vary_values: dict[str, str], now: datetime) -> CacheLookup:
        key = self._make_key(installation_id, path, method, vary_values)
        store = self._entries.get((installation_id, path), {})
        entry = store.get(key)
        if entry and entry.expires_at and now < entry.expires_at:
            entry.hit_count += 1
            return CacheLookup(hit=True, entry=entry)
        return CacheLookup(hit=False)

    def put(self, installation_id: str, path: str, method: str, vary_values: dict[str, str], response_body: str, status_code: int, now: datetime) -> CacheEntry:
        config = self._configs.get((installation_id, path))
        ttl = config.ttl_seconds if config else 60
        key = self._make_key(installation_id, path, method, vary_values)
        entry = CacheEntry(cache_key=key, response_body=response_body, status_code=status_code, created_at=now, expires_at=now + timedelta(seconds=ttl))
        ikey = (installation_id, path)
        if ikey not in self._entries:
            self._entries[ikey] = {}
        self._entries[ikey][key] = entry
        return entry

    def invalidate(self, installation_id: str, path: str) -> int:
        ikey = (installation_id, path)
        count = len(self._entries.get(ikey, {}))
        self._entries.pop(ikey, None)
        return count

    def stats(self, installation_id: str) -> dict[str, int]:
        total = sum(len(v) for (inst, _), v in self._entries.items() if inst == installation_id)
        hits = sum(e.hit_count for (inst, _), v in self._entries.items() if inst == installation_id for e in v.values())
        return {"entries": total, "total_hits": hits}
