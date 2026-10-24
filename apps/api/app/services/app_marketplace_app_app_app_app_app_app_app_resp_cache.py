"""Platform response cache — cache API responses with ETags."""
from __future__ import annotations
import hashlib, time


class ResponseCache:
    def __init__(self, default_ttl: int = 300):
        self._cache: dict[str, dict] = {}
        self._ttl = default_ttl
        self._hits = 0
        self._misses = 0

    def get(self, key: str, etag: str = "", now: float | None = None) -> dict:
        now = now or time.time()
        entry = self._cache.get(key)
        if not entry or now > entry["expires_at"]:
            self._misses += 1
            return {"hit": False}
        if etag and etag == entry["etag"]:
            self._hits += 1
            return {"hit": True, "not_modified": True, "etag": entry["etag"]}
        self._hits += 1
        return {"hit": True, "not_modified": False, "body": entry["body"], "etag": entry["etag"]}

    def set(self, key: str, body: str, ttl: int | None = None) -> dict:
        etag = hashlib.md5(body.encode()).hexdigest()[:16]
        self._cache[key] = {"body": body, "etag": etag,
                             "expires_at": time.time() + (ttl or self._ttl)}
        return {"cached": True, "key": key, "etag": etag}

    def invalidate(self, key: str) -> dict:
        removed = key in self._cache
        self._cache.pop(key, None)
        return {"invalidated": removed, "key": key}

    def stats(self) -> dict:
        total = self._hits + self._misses
        return {"entries": len(self._cache), "hits": self._hits, "misses": self._misses,
                "hit_rate": round(self._hits / max(total, 1) * 100, 1)}
