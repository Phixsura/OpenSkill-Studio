"""API Consumer Request Quota Manager — unified quota management with rollover."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class QuotaWindow:
    consumer_id: str
    window_type: str  # "minute", "hour", "day", "month"
    limit: int
    used: int = 0
    rollover_from_previous: int = 0

    @property
    def total_available(self) -> int:
        return self.limit + self.rollover_from_previous

    @property
    def remaining(self) -> int:
        return max(0, self.total_available - self.used)

    @property
    def usage_pct(self) -> float:
        if self.total_available == 0: return 0.0
        return round((self.used / self.total_available) * 100, 1)

    @property
    def exhausted(self) -> bool:
        return self.used >= self.total_available

VALID_WINDOWS = {"minute", "hour", "day", "month"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestQuotaManager:
    def __init__(self) -> None:
        self._quotas: dict[tuple[str, str, str], QuotaWindow] = {}

    def set_quota(self, installation_id: str, consumer_id: str, window_type: str, limit: int, rollover: int = 0) -> QuotaWindow:
        if not installation_id: raise ValueError("installation_id is required")
        if window_type not in VALID_WINDOWS: raise ValueError(f"Invalid window: {window_type}")
        if limit < 1: raise ValueError("limit must be >= 1")
        if rollover < 0: raise ValueError("rollover must be >= 0")
        q = QuotaWindow(consumer_id=consumer_id, window_type=window_type, limit=limit, rollover_from_previous=rollover)
        self._quotas[(installation_id, consumer_id, window_type)] = q
        return q

    def consume(self, installation_id: str, consumer_id: str, window_type: str, count: int = 1) -> QuotaWindow:
        key = (installation_id, consumer_id, window_type)
        q = self._quotas.get(key)
        if q is None: raise KeyError(f"No quota for {consumer_id}/{window_type}")
        if count < 1: raise ValueError("count must be >= 1")
        if count > q.remaining: raise ValueError("Quota exceeded")
        q.used += count
        return q

    def check(self, installation_id: str, consumer_id: str, window_type: str) -> dict[str, object]:
        q = self._quotas.get((installation_id, consumer_id, window_type))
        if q is None: return {"has_quota": False}
        return {"has_quota": True, "remaining": q.remaining, "usage_pct": q.usage_pct, "exhausted": q.exhausted}

    def reset(self, installation_id: str, consumer_id: str, window_type: str, rollover_unused: bool = False) -> QuotaWindow:
        key = (installation_id, consumer_id, window_type)
        q = self._quotas.get(key)
        if q is None: raise KeyError(f"No quota for {consumer_id}/{window_type}")
        rollover = q.remaining if rollover_unused else 0
        q.used = 0
        q.rollover_from_previous = rollover
        return q

    def near_limit(self, installation_id: str, threshold_pct: float = 80.0) -> list[QuotaWindow]:
        return [q for (inst, _, _), q in self._quotas.items() if inst == installation_id and q.usage_pct >= threshold_pct and not q.exhausted]

    def list_quotas(self, installation_id: str) -> list[QuotaWindow]:
        return [q for (inst, _, _), q in self._quotas.items() if inst == installation_id]
