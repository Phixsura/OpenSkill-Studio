"""Cache invalidation engine — tag-based cache invalidation."""
from __future__ import annotations
import time


class CacheInvalidator:
    def __init__(self):
        self._cache: dict[str, dict] = {}

    def set(self, key: str, value: str, tags: list[str], ttl: int = 300) -> dict:
        self._cache[key] = {"value": value, "tags": tags,
                            "created_at": time.time(), "ttl": ttl}
        return {"key": key, "cached": True}

    def get(self, key: str, now: float | None = None) -> dict:
        now = now or time.time()
        entry = self._cache.get(key)
        if not entry:
            return {"key": key, "hit": False}
        if now - entry["created_at"] > entry["ttl"]:
            del self._cache[key]
            return {"key": key, "hit": False, "reason": "expired"}
        return {"key": key, "hit": True, "value": entry["value"]}

    def invalidate_tag(self, tag: str) -> dict:
        keys_removed = []
        for key in list(self._cache.keys()):
            if tag in self._cache[key]["tags"]:
                del self._cache[key]
                keys_removed.append(key)
        return {"tag": tag, "invalidated": len(keys_removed), "keys": keys_removed}

    def stats(self) -> dict:
        all_tags = set()
        for e in self._cache.values():
            all_tags.update(e["tags"])
        return {"entries": len(self._cache), "unique_tags": len(all_tags)}
