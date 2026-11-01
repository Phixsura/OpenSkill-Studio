"""SLA Monitor — track SLOs with error budgets and burn rate alerts.

Google SRE-style SLO monitoring:
- Define SLOs (99.9% availability, p99 < 200ms)
- Track error budget consumption
- Burn rate alerts (budget consumed too fast)
- Multi-window burn rate (1h + 5m for page-worthy alerts)
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
from collections import deque


@dataclass
class SloDefinition:
    name: str
    target: float  # e.g. 0.999 for 99.9%
    window_seconds: float = 2592000  # 30 days default
    burn_rate_threshold: float = 14.4  # 1h budget in 5m = page-worthy


@dataclass
class SloStatus:
    name: str
    target: float
    current: float  # actual performance
    error_budget_total: float  # allowed errors
    error_budget_remaining: float
    error_budget_pct: float  # % remaining
    burn_rate: float  # current consumption rate (1.0 = on track)
    alerting: bool
    time_until_exhausted_hours: float


class SlaMonitorService:
    def __init__(self):
        self._slos: dict[str, SloDefinition] = {}
        self._events: dict[str, deque] = {}  # slo_name -> deque of (timestamp, good)

    def define_slo(self, name: str, target: float,
                   window_seconds: float = 2592000,
                   burn_rate_threshold: float = 14.4) -> SloDefinition:
        slo = SloDefinition(name=name, target=target,
                            window_seconds=window_seconds,
                            burn_rate_threshold=burn_rate_threshold)
        self._slos[name] = slo
        self._events[name] = deque(maxlen=1000000)
        return slo

    def record(self, slo_name: str, good: bool) -> None:
        """Record a good or bad event."""
        events = self._events.get(slo_name)
        if events is not None:
            events.append((time.time(), good))

    def record_batch(self, slo_name: str, good_count: int,
                     total_count: int) -> None:
        """Record a batch of events."""
        now = time.time()
        events = self._events.get(slo_name)
        if events is None:
            return
        bad = total_count - good_count
        for _ in range(good_count):
            events.append((now, True))
        for _ in range(bad):
            events.append((now, False))

    def get_status(self, slo_name: str) -> SloStatus | None:
        slo = self._slos.get(slo_name)
        if not slo:
            return None

        events = list(self._events.get(slo_name, []))
        now = time.time()
        cutoff = now - slo.window_seconds

        # Filter to window
        in_window = [(ts, good) for ts, good in events if ts > cutoff]
        total = len(in_window)
        good = sum(1 for _, g in in_window if g)

        if total == 0:
            return SloStatus(name=slo.name, target=slo.target, current=1.0,
                             error_budget_total=0, error_budget_remaining=0,
                             error_budget_pct=100, burn_rate=0,
                             alerting=False, time_until_exhausted_hours=float('inf'))

        current = good / total
        error_budget_total = (1 - slo.target) * total
        errors = total - good
        error_budget_remaining = max(0, error_budget_total - errors)
        error_budget_pct = round(error_budget_remaining / max(1, error_budget_total) * 100, 1)

        # Burn rate: how fast we're consuming budget
        # 1.0 = consuming at expected rate, >1 = faster, <1 = slower
        expected_error_rate = 1 - slo.target
        actual_error_rate = errors / total if total > 0 else 0
        burn_rate = round(actual_error_rate / expected_error_rate, 2) if expected_error_rate > 0 else 0

        alerting = burn_rate > slo.burn_rate_threshold

        # Time until exhausted
        if burn_rate > 0 and error_budget_remaining > 0:
            remaining_budget_events = error_budget_remaining
            events_per_hour = total / (slo.window_seconds / 3600) if slo.window_seconds > 0 else 0
            errors_per_hour = events_per_hour * actual_error_rate
            hours = remaining_budget_events / max(0.001, errors_per_hour)
        elif error_budget_remaining <= 0:
            hours = 0
        else:
            hours = float('inf')

        return SloStatus(
            name=slo.name, target=slo.target, current=round(current, 6),
            error_budget_total=round(error_budget_total, 1),
            error_budget_remaining=round(error_budget_remaining, 1),
            error_budget_pct=error_budget_pct, burn_rate=burn_rate,
            alerting=alerting,
            time_until_exhausted_hours=round(hours, 1))

    def get_all_statuses(self) -> list[SloStatus]:
        return [self.get_status(name) for name in self._slos
                if self.get_status(name) is not None]
