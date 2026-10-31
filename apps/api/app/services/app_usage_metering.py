"""App Usage Metering — meter and aggregate API usage.

Manages usage metering:
- Record usage events by metric
- Aggregate by time period (hourly, daily)
- Per-metric totals and averages
- Per-installation scoped meters
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class UsageEvent:
    """A usage event."""

    metric: str
    value: float
    period: str  # "2024-01-15T14" (hourly) or "2024-01-15" (daily)


class AppUsageMetering:
    """Meter and aggregate API usage."""

    def __init__(self) -> None:
        # (installation_id, metric, period) → accumulated value
        self._meters: dict[tuple[str, str, str], float] = {}

    def record(
        self, installation_id: str, metric: str, value: float, period: str,
    ) -> float:
        """Record a usage event. Returns new total for period."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not metric:
            raise ValueError("metric is required")
        if value < 0:
            raise ValueError("value must be non-negative")

        key = (installation_id, metric, period)
        self._meters[key] = self._meters.get(key, 0) + value
        return self._meters[key]

    def get_total(self, installation_id: str, metric: str, period: str) -> float:
        return self._meters.get((installation_id, metric, period), 0)

    def get_metric_total(self, installation_id: str, metric: str) -> float:
        """Total across all periods for a metric."""
        return sum(
            v for (inst, m, _), v in self._meters.items()
            if inst == installation_id and m == metric
        )

    def get_periods(self, installation_id: str, metric: str) -> list[dict]:
        """Get all periods for a metric, sorted."""
        periods = []
        for (inst, m, p), v in self._meters.items():
            if inst == installation_id and m == metric:
                periods.append({"period": p, "value": round(v, 2)})
        return sorted(periods, key=lambda x: x["period"])

    def list_metrics(self, installation_id: str) -> list[str]:
        metrics: set[str] = set()
        for (inst, m, _) in self._meters:
            if inst == installation_id:
                metrics.add(m)
        return sorted(metrics)

    def summary(self, installation_id: str) -> list[dict]:
        """Summary of all metrics with totals."""
        metrics = self.list_metrics(installation_id)
        return [
            {"metric": m, "total": round(self.get_metric_total(installation_id, m), 2),
             "periods": len(self.get_periods(installation_id, m))}
            for m in metrics
        ]
