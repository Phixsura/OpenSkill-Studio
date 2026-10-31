"""App API Developer Consumer Rate Limit Status — real-time rate limit status per consumer."""
from __future__ import annotations
from dataclasses import dataclass
import time
import structlog

log = structlog.get_logger()

@dataclass
class RateLimitStatus:
    consumer_id: str
    endpoint: str
    limit: int
    remaining: int
    reset_at: float
    throttled: bool = False

    @property
    def usage_pct(self) -> float:
        return round((self.limit - self.remaining) / self.limit * 100, 1) if self.limit > 0 else 0.0

    @property
    def seconds_until_reset(self) -> float:
        return max(0.0, round(self.reset_at - time.time(), 1))

class AppAPIDeveloperAPIApiDeveloperApiApiConsumerRateLimitStatus:
    def __init__(self) -> None:
        self._statuses: dict[tuple[str, str, str], RateLimitStatus] = {}

    def update(self, installation_id: str, consumer_id: str, endpoint: str, limit: int, remaining: int, reset_at: float) -> RateLimitStatus:
        if not installation_id: raise ValueError("installation_id is required")
        if limit < 0: raise ValueError("limit must be non-negative")
        throttled = remaining <= 0
        s = RateLimitStatus(consumer_id=consumer_id, endpoint=endpoint, limit=limit, remaining=max(0, remaining), reset_at=reset_at, throttled=throttled)
        self._statuses[(installation_id, consumer_id, endpoint)] = s
        return s

    def get(self, installation_id: str, consumer_id: str, endpoint: str) -> RateLimitStatus | None:
        return self._statuses.get((installation_id, consumer_id, endpoint))

    def throttled_consumers(self, installation_id: str) -> list[RateLimitStatus]:
        return [s for (inst, _, _), s in self._statuses.items() if inst == installation_id and s.throttled]

    def consumer_status(self, installation_id: str, consumer_id: str) -> list[RateLimitStatus]:
        return [s for (inst, cid, _), s in self._statuses.items() if inst == installation_id and cid == consumer_id]

    def near_limit(self, installation_id: str, threshold_pct: float = 80) -> list[RateLimitStatus]:
        return [s for (inst, _, _), s in self._statuses.items() if inst == installation_id and s.usage_pct >= threshold_pct and not s.throttled]
