"""App Usage Meter — track and aggregate API usage per installation.

Tracks metered usage for billing and quota enforcement:
- Record usage events by metric (api_calls, storage_bytes, compute_ms, etc.)
- Aggregate by time window (hourly, daily, monthly)
- Quota enforcement with overage detection
- Per-installation and per-metric isolation
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class TimeWindow(str, Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    MONTHLY = "monthly"


@dataclass
class UsageEvent:
    """A single usage event."""

    metric: str
    quantity: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class UsageSummary:
    """Aggregated usage for a metric within a window."""

    metric: str
    total: float
    count: int
    window: TimeWindow
    window_key: str  # e.g. "2026-10-28" for daily


@dataclass
class QuotaConfig:
    """Quota limit for a metric."""

    metric: str
    limit: float
    window: TimeWindow


@dataclass
class QuotaStatus:
    """Current quota status for a metric."""

    metric: str
    used: float
    limit: float
    remaining: float
    exceeded: bool
    usage_pct: float


def _window_key(ts: float, window: TimeWindow) -> str:
    """Compute the window bucket key for a timestamp."""
    import datetime
    dt = datetime.datetime.fromtimestamp(ts, tz=datetime.UTC)
    if window == TimeWindow.HOURLY:
        return dt.strftime("%Y-%m-%dT%H")
    if window == TimeWindow.DAILY:
        return dt.strftime("%Y-%m-%d")
    return dt.strftime("%Y-%m")


class AppUsageMeter:
    """Track and aggregate API usage per installation."""

    def __init__(self) -> None:
        # (installation_id, metric) → list[UsageEvent]
        self._events: dict[tuple[str, str], list[UsageEvent]] = {}
        # (installation_id, metric) → QuotaConfig
        self._quotas: dict[tuple[str, str], QuotaConfig] = {}

    def record(
        self,
        installation_id: str,
        metric: str,
        quantity: float = 1.0,
        now: float | None = None,
    ) -> UsageEvent:
        """Record a usage event."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not metric:
            raise ValueError("metric is required")
        if quantity <= 0:
            raise ValueError("quantity must be positive")

        event = UsageEvent(
            metric=metric,
            quantity=quantity,
            timestamp=now or time.time(),
        )
        key = (installation_id, metric)
        self._events.setdefault(key, []).append(event)
        return event

    def get_usage(
        self,
        installation_id: str,
        metric: str,
        window: TimeWindow,
        window_key: str | None = None,
        now: float | None = None,
    ) -> UsageSummary:
        """Get aggregated usage for a metric in a time window."""
        now = now or time.time()
        wk = window_key or _window_key(now, window)

        key = (installation_id, metric)
        events = self._events.get(key, [])

        matching = [
            e for e in events if _window_key(e.timestamp, window) == wk
        ]

        return UsageSummary(
            metric=metric,
            total=sum(e.quantity for e in matching),
            count=len(matching),
            window=window,
            window_key=wk,
        )

    def set_quota(
        self,
        installation_id: str,
        metric: str,
        limit: float,
        window: TimeWindow,
    ) -> QuotaConfig:
        """Set a usage quota for a metric."""
        if limit <= 0:
            raise ValueError("limit must be positive")
        quota = QuotaConfig(metric=metric, limit=limit, window=window)
        self._quotas[(installation_id, metric)] = quota
        return quota

    def check_quota(
        self,
        installation_id: str,
        metric: str,
        now: float | None = None,
    ) -> QuotaStatus:
        """Check current quota status for a metric."""
        key = (installation_id, metric)
        quota = self._quotas.get(key)
        if quota is None:
            raise KeyError(f"No quota set for metric {metric}")

        now = now or time.time()
        usage = self.get_usage(installation_id, metric, quota.window, now=now)

        remaining = max(0.0, quota.limit - usage.total)
        return QuotaStatus(
            metric=metric,
            used=usage.total,
            limit=quota.limit,
            remaining=remaining,
            exceeded=usage.total >= quota.limit,
            usage_pct=round(min(usage.total / quota.limit * 100, 100), 2)
            if quota.limit > 0
            else 100.0,
        )

    def can_consume(
        self,
        installation_id: str,
        metric: str,
        quantity: float = 1.0,
        now: float | None = None,
    ) -> bool:
        """Check if consuming quantity would stay within quota."""
        key = (installation_id, metric)
        quota = self._quotas.get(key)
        if quota is None:
            return True  # no quota = unlimited

        now = now or time.time()
        usage = self.get_usage(installation_id, metric, quota.window, now=now)
        return (usage.total + quantity) <= quota.limit

    def list_metrics(self, installation_id: str) -> list[str]:
        """List all tracked metrics for an installation."""
        return list({
            metric for (inst, metric) in self._events if inst == installation_id
        })

    def get_total(self, installation_id: str, metric: str) -> float:
        """Get all-time total for a metric."""
        key = (installation_id, metric)
        events = self._events.get(key, [])
        return sum(e.quantity for e in events)
