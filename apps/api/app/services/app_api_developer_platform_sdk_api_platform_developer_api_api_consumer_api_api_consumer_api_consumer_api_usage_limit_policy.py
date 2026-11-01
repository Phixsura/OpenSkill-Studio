"""Consumer API Usage Limit Policy — define and enforce hierarchical usage limits."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import structlog

log = structlog.get_logger()

@dataclass
class UsageLimit:
    limit_id: str
    consumer_id: str
    metric: str  # "requests", "bandwidth_bytes", "compute_ms"
    period: str  # "minute", "hour", "day", "month"
    max_value: int
    current_value: int = 0
    reset_at: datetime | None = None

@dataclass
class LimitCheckResult:
    allowed: bool
    metric: str
    current: int
    limit: int
    remaining: int
    reset_at: datetime | None = None

PERIOD_DURATIONS = {"minute": timedelta(minutes=1), "hour": timedelta(hours=1), "day": timedelta(days=1), "month": timedelta(days=30)}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiUsageLimitPolicy:
    def __init__(self) -> None:
        self._limits: dict[tuple[str, str, str, str], UsageLimit] = {}  # (inst, consumer, metric, period)

    def set_limit(self, installation_id: str, limit: UsageLimit) -> UsageLimit:
        if not installation_id:
            raise ValueError("installation_id is required")
        if limit.period not in PERIOD_DURATIONS:
            raise ValueError(f"Invalid period: {limit.period}")
        if limit.max_value < 1:
            raise ValueError("max_value must be positive")
        key = (installation_id, limit.consumer_id, limit.metric, limit.period)
        self._limits[key] = limit
        return limit

    def consume(self, installation_id: str, consumer_id: str, metric: str, amount: int, now: datetime) -> LimitCheckResult:
        if amount < 0:
            raise ValueError("amount must be non-negative")
        # Find the most restrictive matching limit
        results: list[LimitCheckResult] = []
        for period in PERIOD_DURATIONS:
            key = (installation_id, consumer_id, metric, period)
            limit = self._limits.get(key)
            if not limit:
                continue
            # Auto-reset if period expired
            if limit.reset_at and now >= limit.reset_at:
                limit.current_value = 0
                limit.reset_at = now + PERIOD_DURATIONS[period]
            elif not limit.reset_at:
                limit.reset_at = now + PERIOD_DURATIONS[period]
            remaining = limit.max_value - limit.current_value
            if amount > remaining:
                results.append(LimitCheckResult(allowed=False, metric=metric, current=limit.current_value, limit=limit.max_value, remaining=remaining, reset_at=limit.reset_at))
            else:
                limit.current_value += amount
                results.append(LimitCheckResult(allowed=True, metric=metric, current=limit.current_value, limit=limit.max_value, remaining=limit.max_value - limit.current_value, reset_at=limit.reset_at))
        if not results:
            return LimitCheckResult(allowed=True, metric=metric, current=0, limit=0, remaining=0)
        # Return the most restrictive (any denied = denied)
        denied = [r for r in results if not r.allowed]
        return denied[0] if denied else min(results, key=lambda r: r.remaining)

    def get_usage(self, installation_id: str, consumer_id: str) -> list[UsageLimit]:
        return [l for (inst, cid, _, _), l in self._limits.items() if inst == installation_id and cid == consumer_id]
