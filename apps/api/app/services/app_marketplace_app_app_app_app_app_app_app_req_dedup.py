"""Request deduplication — detect and suppress duplicate API requests."""
from __future__ import annotations
import hashlib, time


class RequestDeduplicator:
    def __init__(self, ttl_seconds: int = 60):
        self._seen: dict[str, float] = {}
        self._ttl = ttl_seconds

    def _key(self, method: str, path: str, body_hash: str) -> str:
        return hashlib.sha256(f"{method}:{path}:{body_hash}".encode()).hexdigest()[:16]

    def _prune(self, now: float) -> None:
        expired = [k for k, t in self._seen.items() if now - t > self._ttl]
        for k in expired:
            del self._seen[k]

    def check(self, method: str, path: str, body_hash: str) -> dict:
        now = time.time()
        self._prune(now)
        key = self._key(method, path, body_hash)
        is_dup = key in self._seen
        if not is_dup:
            self._seen[key] = now
        return {"key": key, "is_duplicate": is_dup, "cache_size": len(self._seen)}

    def stats(self) -> dict:
        return {"cached_keys": len(self._seen), "ttl_seconds": self._ttl}
