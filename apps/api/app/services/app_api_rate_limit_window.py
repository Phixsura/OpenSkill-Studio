"""App API Rate Limit Window — sliding window rate limiter.

Manages rate limiting with sliding windows:
- Fixed and sliding window strategies
- Per-consumer tracking
- Remaining quota calculation
- Per-installation scoped windows
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class WindowState:
    """State for a rate limit window."""

    count: int = 0
    window_start: float = field(default_factory=time.time)


class AppAPIRateLimitWindow:
    """Sliding window rate limiter."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60) -> None:
        self._max = max_requests
        self._window = window_seconds
        self._state: dict[tuple[str, str], WindowState] = {}

    def check(self, installation_id: str, consumer_id: str) -> dict:
        """Check and record a request. Returns {allowed, remaining, reset_in}."""
        now = time.time()
        key = (installation_id, consumer_id)
        state = self._state.get(key)

        if state is None or (now - state.window_start) >= self._window:
            self._state[key] = WindowState(count=1, window_start=now)
            return {"allowed": True, "remaining": self._max - 1, "reset_in": self._window}

        if state.count >= self._max:
            reset_in = round(self._window - (now - state.window_start), 1)
            return {"allowed": False, "remaining": 0, "reset_in": max(0, reset_in)}

        state.count += 1
        reset_in = round(self._window - (now - state.window_start), 1)
        return {"allowed": True, "remaining": self._max - state.count, "reset_in": max(0, reset_in)}

    def reset(self, installation_id: str, consumer_id: str) -> None:
        key = (installation_id, consumer_id)
        if key in self._state:
            del self._state[key]

    def current_usage(self, installation_id: str, consumer_id: str) -> int:
        state = self._state.get((installation_id, consumer_id))
        return state.count if state else 0
