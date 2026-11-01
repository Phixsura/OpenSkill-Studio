"""Rate limiter middleware — sliding window rate limiter for app APIs."""

import time
from collections import defaultdict


class SlidingWindowRateLimiter:
    def __init__(self, *, limit: int = 100, window_seconds: int = 60) -> None:
        self._limit = limit
        self._window = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, key: str) -> dict:
        now = time.time()
        cutoff = now - self._window
        self._requests[key] = [t for t in self._requests[key] if t > cutoff]
        current = len(self._requests[key])
        if current >= self._limit:
            return {"allowed": False, "remaining": 0, "retry_after": round(self._requests[key][0] - cutoff, 1)}
        self._requests[key].append(now)
        return {"allowed": True, "remaining": self._limit - current - 1, "retry_after": None}

    def get_usage(self, key: str) -> dict:
        now = time.time()
        cutoff = now - self._window
        active = [t for t in self._requests.get(key, []) if t > cutoff]
        return {"current": len(active), "limit": self._limit, "window_seconds": self._window}
