"""App Sliding Window Rate Limiter — precise sliding-window request counting.

Implements sliding window log rate limiting:
- Track individual request timestamps
- Sliding window count over configurable window size
- Per-key isolated counters
- Cleanup of expired entries
- Remaining quota and reset time computation
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class WindowResult:
    """Result of a rate limit check."""

    allowed: bool
    count: int
    limit: int
    remaining: int
    reset_at: float  # timestamp when window resets


class AppSlidingWindowLimiter:
    """Sliding window log rate limiter."""

    def __init__(self, limit: int = 100, window_seconds: float = 60.0) -> None:
        if limit < 1:
            raise ValueError("limit must be >= 1")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be > 0")
        self._limit = limit
        self._window = window_seconds
        # key → sorted list of timestamps
        self._logs: dict[str, list[float]] = {}

    def check(self, key: str, now: float | None = None) -> WindowResult:
        """Check rate limit without consuming a request."""
        now = now or time.time()
        self._trim(key, now)
        timestamps = self._logs.get(key, [])
        count = len(timestamps)
        remaining = max(0, self._limit - count)
        reset_at = (timestamps[0] + self._window) if timestamps else now + self._window
        return WindowResult(
            allowed=count < self._limit,
            count=count,
            limit=self._limit,
            remaining=remaining,
            reset_at=reset_at,
        )

    def hit(self, key: str, now: float | None = None) -> WindowResult:
        """Record a request and check the limit."""
        now = now or time.time()
        self._trim(key, now)
        timestamps = self._logs.setdefault(key, [])
        count = len(timestamps)

        if count >= self._limit:
            reset_at = timestamps[0] + self._window
            return WindowResult(
                allowed=False,
                count=count,
                limit=self._limit,
                remaining=0,
                reset_at=reset_at,
            )

        timestamps.append(now)
        count += 1
        remaining = max(0, self._limit - count)
        reset_at = timestamps[0] + self._window
        return WindowResult(
            allowed=True,
            count=count,
            limit=self._limit,
            remaining=remaining,
            reset_at=reset_at,
        )

    def reset(self, key: str) -> None:
        """Reset rate limit for a key."""
        self._logs.pop(key, None)

    def get_count(self, key: str, now: float | None = None) -> int:
        """Get current request count in the window."""
        now = now or time.time()
        self._trim(key, now)
        return len(self._logs.get(key, []))

    def cleanup(self, now: float | None = None) -> int:
        """Remove all expired entries. Returns count of keys cleaned."""
        now = now or time.time()
        cleaned = 0
        empty_keys = []
        for key in self._logs:
            self._trim(key, now)
            if not self._logs[key]:
                empty_keys.append(key)
        for key in empty_keys:
            del self._logs[key]
            cleaned += 1
        return cleaned

    def _trim(self, key: str, now: float) -> None:
        """Remove timestamps outside the window."""
        timestamps = self._logs.get(key)
        if timestamps is None:
            return
        cutoff = now - self._window
        while timestamps and timestamps[0] <= cutoff:
            timestamps.pop(0)
