"""App Analytics Aggregator — compute daily/weekly/monthly metrics for installed apps.

Provides analytics for the developer platform:
- DAU/WAU/MAU tracking per app
- Event counting by type (installs, uninstalls, API calls, errors)
- Trend detection (growth rate, churn rate)
- Top-N rankings by metric
- Time-series data for charting
- Retention cohort computation
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum

import structlog

log = structlog.get_logger()


class MetricType(str, Enum):
    INSTALL = "install"
    UNINSTALL = "uninstall"
    API_CALL = "api_call"
    ERROR = "error"
    ACTIVE_USER = "active_user"


class Period(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


@dataclass
class MetricEvent:
    """A single metric event."""

    app_id: str
    metric_type: MetricType
    value: int = 1
    user_id: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class TimePoint:
    """A single point in a time series."""

    period_key: str   # e.g. "2026-10-28" or "2026-W43"
    value: int


@dataclass
class AppMetricsSummary:
    """Aggregated metrics for an app."""

    app_id: str
    period: Period
    total_installs: int
    total_uninstalls: int
    total_api_calls: int
    total_errors: int
    active_users: int
    error_rate: float
    growth_rate: float        # installs - uninstalls / installs
    net_installs: int


@dataclass
class TopAppEntry:
    """A ranking entry."""

    app_id: str
    value: int
    rank: int


def _day_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


def _week_key(dt: datetime) -> str:
    return dt.strftime("%Y-W%W")


def _month_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m")


def _period_key(dt: datetime, period: Period) -> str:
    if period == Period.DAY:
        return _day_key(dt)
    elif period == Period.WEEK:
        return _week_key(dt)
    return _month_key(dt)


class AppAnalyticsAggregator:
    """Aggregate and query app metrics."""

    def __init__(self):
        # (app_id, metric_type, period_key) → total
        self._counters: dict[tuple[str, MetricType, str], int] = defaultdict(int)
        # (app_id, period_key) → set of user_ids (for active user counting)
        self._active_users: dict[tuple[str, str], set[str]] = defaultdict(set)
        # All events for time-series
        self._events: list[MetricEvent] = []

    def record(self, event: MetricEvent) -> None:
        """Record a metric event."""
        for period in Period:
            pk = _period_key(event.timestamp, period)
            key = (event.app_id, event.metric_type, pk)
            self._counters[key] += event.value

            if event.user_id:
                self._active_users[(event.app_id, pk)].add(event.user_id)

        self._events.append(event)

    def record_batch(self, events: list[MetricEvent]) -> int:
        """Record multiple events. Returns count processed."""
        for e in events:
            self.record(e)
        return len(events)

    # ── Queries ──────────────────────────────────────────

    def get_count(self, app_id: str, metric_type: MetricType, period: Period,
                  dt: datetime | None = None) -> int:
        dt = dt or datetime.now(UTC)
        pk = _period_key(dt, period)
        return self._counters.get((app_id, metric_type, pk), 0)

    def get_active_users(self, app_id: str, period: Period,
                         dt: datetime | None = None) -> int:
        dt = dt or datetime.now(UTC)
        pk = _period_key(dt, period)
        return len(self._active_users.get((app_id, pk), set()))

    def get_summary(self, app_id: str, period: Period,
                    dt: datetime | None = None) -> AppMetricsSummary:
        """Get aggregated summary for an app and period."""
        dt = dt or datetime.now(UTC)
        pk = _period_key(dt, period)

        installs = self._counters.get((app_id, MetricType.INSTALL, pk), 0)
        uninstalls = self._counters.get((app_id, MetricType.UNINSTALL, pk), 0)
        api_calls = self._counters.get((app_id, MetricType.API_CALL, pk), 0)
        errors = self._counters.get((app_id, MetricType.ERROR, pk), 0)
        active = len(self._active_users.get((app_id, pk), set()))

        error_rate = (errors / api_calls * 100) if api_calls > 0 else 0.0
        growth_rate = ((installs - uninstalls) / installs * 100) if installs > 0 else 0.0

        return AppMetricsSummary(
            app_id=app_id,
            period=period,
            total_installs=installs,
            total_uninstalls=uninstalls,
            total_api_calls=api_calls,
            total_errors=errors,
            active_users=active,
            error_rate=round(error_rate, 2),
            growth_rate=round(growth_rate, 2),
            net_installs=installs - uninstalls,
        )

    def get_time_series(self, app_id: str, metric_type: MetricType,
                        period: Period, periods: int = 7,
                        end_dt: datetime | None = None) -> list[TimePoint]:
        """Get time-series data for charting."""
        end_dt = end_dt or datetime.now(UTC)
        points: list[TimePoint] = []

        if period == Period.DAY:
            delta = timedelta(days=1)
        elif period == Period.WEEK:
            delta = timedelta(weeks=1)
        else:
            delta = timedelta(days=30)

        for i in range(periods - 1, -1, -1):
            dt = end_dt - delta * i
            pk = _period_key(dt, period)
            value = self._counters.get((app_id, metric_type, pk), 0)
            points.append(TimePoint(period_key=pk, value=value))

        return points

    def top_apps(self, metric_type: MetricType, period: Period,
                 limit: int = 10, dt: datetime | None = None) -> list[TopAppEntry]:
        """Get top N apps by a metric for a period."""
        dt = dt or datetime.now(UTC)
        pk = _period_key(dt, period)

        app_values: Counter = Counter()
        for (aid, mt, p), val in self._counters.items():
            if mt == metric_type and p == pk:
                app_values[aid] += val

        ranked = app_values.most_common(limit)
        return [
            TopAppEntry(app_id=aid, value=val, rank=i + 1)
            for i, (aid, val) in enumerate(ranked)
        ]
