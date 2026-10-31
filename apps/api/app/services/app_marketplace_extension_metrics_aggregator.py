"""Metrics Aggregator — aggregate extension metrics across time periods.

Consolidates raw event data into hourly, daily, and monthly aggregates
for dashboards and analytics reports.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class MetricPoint:
    timestamp: str  # ISO date or period key
    value: float
    count: int = 1


class MetricsAggregator:
    """Aggregates raw metrics into time-bucketed summaries."""

    def __init__(self):
        self._raw: dict[str, list[MetricPoint]] = defaultdict(list)

    def record(self, metric_name: str, value: float, timestamp: str) -> None:
        """Record a raw metric value with timestamp."""
        self._raw[metric_name].append(MetricPoint(timestamp, value))

    def aggregate_by_period(self, metric_name: str, period: str = "daily") -> list[dict]:
        """Aggregate metrics by period (hourly, daily, monthly)."""
        points = self._raw.get(metric_name, [])
        if not points:
            return []

        buckets: dict[str, list[float]] = defaultdict(list)
        for p in points:
            key = self._bucket_key(p.timestamp, period)
            buckets[key].append(p.value)

        return [
            {"period": key,
             "count": len(vals),
             "sum": round(sum(vals), 2),
             "avg": round(sum(vals) / len(vals), 2),
             "min": round(min(vals), 2),
             "max": round(max(vals), 2)}
            for key, vals in sorted(buckets.items())
        ]

    def get_totals(self, metric_name: str) -> dict:
        """Get overall totals for a metric."""
        points = self._raw.get(metric_name, [])
        if not points:
            return {"count": 0, "sum": 0, "avg": 0, "min": 0, "max": 0}
        vals = [p.value for p in points]
        return {
            "count": len(vals),
            "sum": round(sum(vals), 2),
            "avg": round(sum(vals) / len(vals), 2),
            "min": round(min(vals), 2),
            "max": round(max(vals), 2),
        }

    def get_percentiles(self, metric_name: str, percentiles: list[float] | None = None) -> dict:
        """Calculate percentiles (p50, p90, p95, p99)."""
        pcts = percentiles or [50, 90, 95, 99]
        points = self._raw.get(metric_name, [])
        if not points:
            return {f"p{int(p)}": 0 for p in pcts}
        vals = sorted(p.value for p in points)
        n = len(vals)
        return {f"p{int(p)}": round(vals[min(int(n * p / 100), n - 1)], 2) for p in pcts}

    def compare_periods(self, metric_name: str, period_a: str, period_b: str,
                        period_type: str = "daily") -> dict:
        """Compare two periods."""
        aggs = {a["period"]: a for a in self.aggregate_by_period(metric_name, period_type)}
        a = aggs.get(period_a, {"sum": 0, "avg": 0, "count": 0})
        b = aggs.get(period_b, {"sum": 0, "avg": 0, "count": 0})
        delta_sum = b["sum"] - a["sum"]
        pct_change = round(delta_sum / max(0.01, a["sum"]) * 100, 1) if a["sum"] else 0
        return {"period_a": period_a, "period_b": period_b,
                "delta_sum": delta_sum, "pct_change": pct_change}

    def list_metrics(self) -> list[str]:
        return sorted(self._raw.keys())

    def _bucket_key(self, timestamp: str, period: str) -> str:
        if period == "hourly":
            return timestamp[:13]  # 2026-10-25T12
        elif period == "monthly":
            return timestamp[:7]   # 2026-10
        return timestamp[:10]      # 2026-10-25
