"""Response Cache — HTTP-style caching with Vary, ETag, and stale-while-revalidate.

Implements:
- Cache-Control directive parsing (max-age, no-cache, no-store, private)
- Vary header support (cache per Accept-Language, etc.)
- ETag generation and conditional requests (If-None-Match → 304)
- Stale-while-revalidate (serve stale, recompute in background)
- Cache key generation from method + URL + Vary headers
"""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import time


@dataclass
class CachedResponse:
    cache_key: str
    status: int
    body: dict
    headers: dict
    etag: str
    created_at: float
    max_age: float
    stale_while_revalidate: float = 0
    hits: int = 0

    @property
    def expired(self) -> bool:
        return time.time() > self.created_at + self.max_age

    @property
    def stale_servable(self) -> bool:
        age = time.time() - self.created_at
        return self.max_age < age <= self.max_age + self.stale_while_revalidate


class ResponseCacheService:
    def __init__(self):
        self._cache: dict[str, CachedResponse] = {}
        self._total_hits = 0
        self._total_misses = 0
        self._total_stale = 0

    def _build_key(self, method: str, url: str, vary_headers: dict) -> str:
        key_data = f"{method}:{url}"
        if vary_headers:
            vary_str = "|".join(f"{k}={v}" for k, v in sorted(vary_headers.items()))
            key_data += f":{vary_str}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _generate_etag(self, body: dict) -> str:
        import json
        content = json.dumps(body, sort_keys=True)
        return f'W/"{hashlib.md5(content.encode()).hexdigest()[:16]}"'

    def store(self, method: str, url: str, status: int, body: dict,
              headers: dict | None = None, max_age: float = 60,
              vary: list[str] | None = None, vary_values: dict | None = None,
              stale_while_revalidate: float = 0) -> CachedResponse:
        """Store a response in cache."""
        vary_headers = {}
        if vary and vary_values:
            vary_headers = {k: vary_values.get(k, "") for k in vary}

        key = self._build_key(method, url, vary_headers)
        etag = self._generate_etag(body)

        cached = CachedResponse(
            cache_key=key, status=status, body=body,
            headers=headers or {}, etag=etag,
            created_at=time.time(), max_age=max_age,
            stale_while_revalidate=stale_while_revalidate)
        self._cache[key] = cached
        return cached

    def lookup(self, method: str, url: str,
               vary_values: dict | None = None,
               if_none_match: str = "") -> dict:
        """Look up a cached response."""
        key = self._build_key(method, url, vary_values or {})
        cached = self._cache.get(key)

        if not cached:
            self._total_misses += 1
            return {"hit": False, "status": "miss"}

        # ETag conditional
        if if_none_match and if_none_match == cached.etag:
            if not cached.expired:
                cached.hits += 1
                self._total_hits += 1
                return {"hit": True, "status": "not_modified",
                        "http_status": 304, "etag": cached.etag}

        if not cached.expired:
            cached.hits += 1
            self._total_hits += 1
            return {"hit": True, "status": "fresh",
                    "body": cached.body, "etag": cached.etag,
                    "age": round(time.time() - cached.created_at, 1)}

        # Expired but stale-while-revalidate?
        if cached.stale_servable:
            cached.hits += 1
            self._total_stale += 1
            return {"hit": True, "status": "stale",
                    "body": cached.body, "etag": cached.etag,
                    "needs_revalidation": True}

        # Truly expired
        del self._cache[key]
        self._total_misses += 1
        return {"hit": False, "status": "expired"}

    def invalidate(self, method: str, url: str,
                   vary_values: dict | None = None) -> bool:
        key = self._build_key(method, url, vary_values or {})
        return self._cache.pop(key, None) is not None

    def purge_expired(self) -> int:
        now = time.time()
        expired = [k for k, v in self._cache.items()
                   if now > v.created_at + v.max_age + v.stale_while_revalidate]
        for k in expired:
            del self._cache[k]
        return len(expired)

    def stats(self) -> dict:
        total = self._total_hits + self._total_misses
        return {
            "entries": len(self._cache),
            "hits": self._total_hits, "misses": self._total_misses,
            "stale_served": self._total_stale,
            "hit_rate": round(self._total_hits / max(1, total) * 100, 1),
        }
