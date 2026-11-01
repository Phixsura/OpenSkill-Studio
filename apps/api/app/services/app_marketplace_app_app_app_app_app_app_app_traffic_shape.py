"""Traffic shaping — sliding window rate limiter with burst support."""
from __future__ import annotations
import time


class SlidingWindowLimiter:
    def __init__(self, max_requests: int, window_seconds: int, burst: int = 0):
        self._max = max_requests
        self._window = window_seconds
        self._burst = burst
        self._requests: dict[str, list[float]] = {}

    def _prune(self, key: str, now: float) -> None:
        cutoff = now - self._window
        self._requests[key] = [t for t in self._requests.get(key, []) if t > cutoff]

    def allow(self, key: str, now: float | None = None) -> dict:
        now = now or time.time()
        self._prune(key, now)
        count = len(self._requests.get(key, []))
        limit = self._max + self._burst
        allowed = count < limit
        if allowed:
            self._requests.setdefault(key, []).append(now)
        remaining = max(0, limit - count - (1 if allowed else 0))
        return {"allowed": allowed, "remaining": remaining, "limit": limit,
                "current": count + (1 if allowed else 0), "key": key}

    def stats(self) -> dict:
        return {"tracked_keys": len(self._requests),
                "max_requests": self._max, "window_seconds": self._window,
                "burst": self._burst}
