"""App API Usage Quota — track monthly API usage against plan quotas.

Manages usage quotas:
- Track monthly usage per metric
- Compare against plan limits
- Overage detection
- Per-installation scoped quotas
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class UsageQuota:
    """A monthly usage quota."""

    metric: str
    limit: int
    used: int = 0
    period: str = ""  # "2024-01"

    @property
    def remaining(self) -> int:
        return max(0, self.limit - self.used)

    @property
    def usage_pct(self) -> float:
        if self.limit == 0:
            return 100.0 if self.used > 0 else 0.0
        return round(self.used / self.limit * 100, 1)

    @property
    def is_over(self) -> bool:
        return self.used > self.limit


class AppAPIUsageQuota:
    """Track monthly API usage against plan quotas."""

    def __init__(self) -> None:
        self._quotas: dict[tuple[str, str, str], UsageQuota] = {}

    def set_quota(
        self, installation_id: str, metric: str, limit: int, period: str,
    ) -> UsageQuota:
        if not installation_id:
            raise ValueError("installation_id is required")
        if limit < 0:
            raise ValueError("limit must be non-negative")

        q = UsageQuota(metric=metric, limit=limit, period=period)
        self._quotas[(installation_id, metric, period)] = q
        return q

    def increment(
        self, installation_id: str, metric: str, period: str, amount: int = 1,
    ) -> UsageQuota:
        key = (installation_id, metric, period)
        q = self._quotas.get(key)
        if q is None:
            raise KeyError(f"Quota for {metric} in {period} not found")
        if not isinstance(amount, int) or amount < 0:
            raise ValueError("amount must be a non-negative integer")
        q.used += amount
        return q

    def check(self, installation_id: str, metric: str, period: str) -> UsageQuota:
        key = (installation_id, metric, period)
        q = self._quotas.get(key)
        if q is None:
            raise KeyError(f"Quota not found")
        return q

    def overages(self, installation_id: str, period: str) -> list[UsageQuota]:
        return [
            q for (inst, _, p), q in self._quotas.items()
            if inst == installation_id and p == period and q.is_over
        ]

    def summary(self, installation_id: str, period: str) -> list[dict]:
        return [
            {"metric": q.metric, "used": q.used, "limit": q.limit, "pct": q.usage_pct}
            for (inst, _, p), q in self._quotas.items()
            if inst == installation_id and p == period
        ]
