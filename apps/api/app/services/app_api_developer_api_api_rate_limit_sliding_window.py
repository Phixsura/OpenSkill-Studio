"""App API Developer Rate Limit Sliding Window — sliding window rate limiting."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class SlidingWindowCounter:
    consumer_id: str
    window_size_seconds: int
    max_requests: int
    timestamps: list[float] = field(default_factory=list)

    def _prune(self) -> None:
        cutoff = time.time() - self.window_size_seconds
        self.timestamps = [t for t in self.timestamps if t > cutoff]

    @property
    def current_count(self) -> int:
        self._prune()
        return len(self.timestamps)

    @property
    def remaining(self) -> int:
        return max(0, self.max_requests - self.current_count)

    @property
    def is_limited(self) -> bool:
        return self.current_count >= self.max_requests

class AppAPIDeveloperAPIApiRateLimitSlidingWindow:
    def __init__(self) -> None:
        self._windows: dict[tuple[str, str, str], SlidingWindowCounter] = {}

    def configure(self, installation_id: str, consumer_id: str, endpoint: str, window_size_seconds: int, max_requests: int) -> SlidingWindowCounter:
        if not installation_id: raise ValueError("installation_id is required")
        if window_size_seconds < 1: raise ValueError("window must be >= 1 second")
        if max_requests < 1: raise ValueError("max_requests must be >= 1")
        key = (installation_id, consumer_id, endpoint)
        w = SlidingWindowCounter(consumer_id=consumer_id, window_size_seconds=window_size_seconds, max_requests=max_requests)
        self._windows[key] = w
        return w

    def try_request(self, installation_id: str, consumer_id: str, endpoint: str) -> tuple[bool, int]:
        """Returns (allowed, remaining)."""
        key = (installation_id, consumer_id, endpoint)
        w = self._windows.get(key)
        if w is None: return (True, -1)  # no limit configured
        if w.is_limited: return (False, 0)
        w.timestamps.append(time.time())
        return (True, w.remaining)

    def status(self, installation_id: str, consumer_id: str, endpoint: str) -> dict[str, int]:
        key = (installation_id, consumer_id, endpoint)
        w = self._windows.get(key)
        if w is None: return {"configured": 0}
        return {"current": w.current_count, "max": w.max_requests, "remaining": w.remaining}

    def limited_consumers(self, installation_id: str) -> list[str]:
        seen: set[str] = set()
        for (inst, cid, _), w in self._windows.items():
            if inst == installation_id and w.is_limited:
                seen.add(cid)
        return list(seen)
