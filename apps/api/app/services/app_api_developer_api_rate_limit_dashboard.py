"""App API Developer Rate Limit Dashboard — real-time rate limit visibility."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class RateLimitSnapshot:
    endpoint: str
    limit: int
    remaining: int
    reset_at: float
    consumer_id: str = ""

    @property
    def usage_pct(self) -> float:
        return round((self.limit - self.remaining) / self.limit * 100, 1) if self.limit > 0 else 0.0

class AppAPIDeveloperAPIRateLimitDashboard:
    def __init__(self) -> None:
        self._snapshots: dict[str, list[RateLimitSnapshot]] = {}

    def record(self, installation_id: str, endpoint: str, limit: int, remaining: int, reset_at: float, consumer_id: str = "") -> RateLimitSnapshot:
        if not installation_id: raise ValueError("installation_id is required")
        if limit < 0: raise ValueError("limit must be non-negative")
        if remaining < 0: remaining = 0
        s = RateLimitSnapshot(endpoint=endpoint, limit=limit, remaining=remaining, reset_at=reset_at, consumer_id=consumer_id)
        self._snapshots.setdefault(installation_id, []).append(s)
        return s

    def current(self, installation_id: str) -> list[RateLimitSnapshot]:
        now = time.time()
        return [s for s in self._snapshots.get(installation_id, []) if s.reset_at > now]

    def hotspots(self, installation_id: str, threshold_pct: float = 80.0) -> list[RateLimitSnapshot]:
        return [s for s in self._snapshots.get(installation_id, []) if s.usage_pct >= threshold_pct]

    def by_consumer(self, installation_id: str, consumer_id: str) -> list[RateLimitSnapshot]:
        return [s for s in self._snapshots.get(installation_id, []) if s.consumer_id == consumer_id]
