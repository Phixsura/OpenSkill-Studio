"""Service mesh rate limiter — per-service rate limiting in the mesh."""
from __future__ import annotations
import time


class MeshRateLimiter:
    def __init__(self):
        self._limits: dict[str, dict] = {}
        self._counters: dict[str, dict] = {}

    def set_limit(self, source: str, destination: str, rpm: int) -> dict:
        key = f"{source}→{destination}"
        self._limits[key] = {"rpm": rpm}
        self._counters[key] = {"count": 0, "window_start": 0}
        return {"key": key, "rpm": rpm}

    def allow(self, source: str, destination: str, now: float | None = None) -> dict:
        now = now or time.time()
        key = f"{source}→{destination}"
        limit = self._limits.get(key)
        if not limit:
            return {"allowed": True, "reason": "no_limit"}
        counter = self._counters[key]
        if now - counter["window_start"] >= 60:
            counter["count"] = 0
            counter["window_start"] = now
        if counter["count"] >= limit["rpm"]:
            return {"allowed": False, "key": key, "reason": "rate_exceeded"}
        counter["count"] += 1
        return {"allowed": True, "key": key, "remaining": limit["rpm"] - counter["count"]}

    def stats(self) -> dict:
        return {"total_limits": len(self._limits)}
