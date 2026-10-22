"""Cache manager — TTL-based caching for app API responses."""

from datetime import datetime, timezone


class AppCacheManager:
    def __init__(self) -> None:
        self._cache: dict[str, dict] = {}

    def get(self, key: str) -> dict | None:
        entry = self._cache.get(key)
        if not entry:
            return None
        if entry["expires_at"] and datetime.now(timezone.utc).isoformat() > entry["expires_at"]:
            del self._cache[key]
            return None
        entry["hits"] += 1
        return entry["value"]

    def set(self, key: str, value: dict, ttl_seconds: int = 300) -> None:
        from datetime import timedelta
        expires = (datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)).isoformat()
        self._cache[key] = {"value": value, "expires_at": expires, "hits": 0, "set_at": datetime.now(timezone.utc).isoformat()}

    def invalidate(self, key: str) -> bool:
        return self._cache.pop(key, None) is not None

    def clear(self) -> int:
        count = len(self._cache)
        self._cache.clear()
        return count

    def stats(self) -> dict:
        total_hits = sum(e["hits"] for e in self._cache.values())
        return {"entries": len(self._cache), "total_hits": total_hits}
