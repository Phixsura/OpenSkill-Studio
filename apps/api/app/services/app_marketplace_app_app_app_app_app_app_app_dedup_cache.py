"""Request dedup cache — cache recent request results for deduplication."""
from __future__ import annotations
import hashlib, time


class DedupCache:
    def __init__(self, ttl_seconds: int = 60, max_size: int = 10000):
        self._cache: dict[str, dict] = {}
        self._ttl = ttl_seconds
        self._max = max_size
        self._hits = 0
        self._misses = 0

    def _key(self, method: str, path: str, body_hash: str) -> str:
        return hashlib.sha256(f"{method}:{path}:{body_hash}".encode()).hexdigest()[:20]

    def check(self, method: str, path: str, body_hash: str, now: float | None = None) -> dict:
        now = now or time.time()
        key = self._key(method, path, body_hash)
        entry = self._cache.get(key)
        if entry and now - entry["stored_at"] < self._ttl:
            self._hits += 1
            return {"hit": True, "response": entry["response"], "key": key}
        self._misses += 1
        return {"hit": False, "key": key}

    def store(self, method: str, path: str, body_hash: str, response: dict) -> dict:
        key = self._key(method, path, body_hash)
        if len(self._cache) >= self._max:
            oldest = min(self._cache.items(), key=lambda x: x[1]["stored_at"])
            del self._cache[oldest[0]]
        self._cache[key] = {"response": response, "stored_at": time.time()}
        return {"stored": True, "key": key, "cache_size": len(self._cache)}

    def stats(self) -> dict:
        total = self._hits + self._misses
        return {"size": len(self._cache), "hits": self._hits, "misses": self._misses,
                "hit_rate": round(self._hits / max(total, 1) * 100, 1)}
