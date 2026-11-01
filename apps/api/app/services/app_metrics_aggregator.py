"""App Metrics Aggregator — collect and aggregate time-series metrics.

Collects numerical metrics for installed apps:
- Record data points with labels
- Aggregate: sum, avg, min, max, count, p99
- Time-bucketed aggregation (minute, hour, day)
- Per-installation scoped metrics
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class AggregationType(str, Enum):
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    P99 = "p99"


class BucketSize(str, Enum):
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"


@dataclass
class DataPoint:
    """A single metric data point."""

    value: float
    timestamp: float = field(default_factory=time.time)
    labels: dict[str, str] = field(default_factory=dict)


@dataclass
class AggregateResult:
    """Result of aggregating a metric."""

    metric: str
    aggregation: AggregationType
    value: float
    count: int
    bucket: str = ""  # time bucket key


def _bucket_key(ts: float, size: BucketSize) -> str:
    import datetime
    dt = datetime.datetime.fromtimestamp(ts, tz=datetime.UTC)
    if size == BucketSize.MINUTE:
        return dt.strftime("%Y-%m-%dT%H:%M")
    if size == BucketSize.HOUR:
        return dt.strftime("%Y-%m-%dT%H")
    return dt.strftime("%Y-%m-%d")


class AppMetricsAggregator:
    """Collect and aggregate time-series metrics."""

    def __init__(self, max_points_per_metric: int = 10000) -> None:
        # (installation_id, metric) → list[DataPoint]
        self._data: dict[tuple[str, str], list[DataPoint]] = {}
        self._max_points = max(100, max_points_per_metric)

    def record(
        self,
        installation_id: str,
        metric: str,
        value: float,
        labels: dict[str, str] | None = None,
        now: float | None = None,
    ) -> DataPoint:
        """Record a data point."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not metric:
            raise ValueError("metric is required")
        if math.isnan(value) or math.isinf(value):
            raise ValueError("value must be finite")

        point = DataPoint(
            value=value,
            timestamp=now or time.time(),
            labels=labels or {},
        )
        key = (installation_id, metric)
        points = self._data.setdefault(key, [])
        points.append(point)
        if len(points) > self._max_points:
            self._data[key] = points[-self._max_points:]

        return point

    def aggregate(
        self,
        installation_id: str,
        metric: str,
        aggregation: AggregationType,
        since: float | None = None,
        until: float | None = None,
        label_filter: dict[str, str] | None = None,
    ) -> AggregateResult:
        """Aggregate a metric over a time range."""
        points = self._filter_points(installation_id, metric, since, until, label_filter)
        values = [p.value for p in points]

        if not values:
            return AggregateResult(
                metric=metric, aggregation=aggregation, value=0.0, count=0,
            )

        value = self._compute(aggregation, values)
        return AggregateResult(
            metric=metric, aggregation=aggregation,
            value=round(value, 6), count=len(values),
        )

    def aggregate_by_bucket(
        self,
        installation_id: str,
        metric: str,
        aggregation: AggregationType,
        bucket_size: BucketSize,
        since: float | None = None,
        until: float | None = None,
    ) -> list[AggregateResult]:
        """Aggregate a metric grouped by time buckets."""
        points = self._filter_points(installation_id, metric, since, until)
        buckets: dict[str, list[float]] = {}
        for p in points:
            bk = _bucket_key(p.timestamp, bucket_size)
            buckets.setdefault(bk, []).append(p.value)

        results = []
        for bk in sorted(buckets):
            value = self._compute(aggregation, buckets[bk])
            results.append(AggregateResult(
                metric=metric, aggregation=aggregation,
                value=round(value, 6), count=len(buckets[bk]),
                bucket=bk,
            ))
        return results

    def list_metrics(self, installation_id: str) -> list[str]:
        return sorted({
            metric for (inst, metric) in self._data if inst == installation_id
        })

    def point_count(self, installation_id: str, metric: str) -> int:
        return len(self._data.get((installation_id, metric), []))

    def _filter_points(
        self,
        installation_id: str,
        metric: str,
        since: float | None = None,
        until: float | None = None,
        label_filter: dict[str, str] | None = None,
    ) -> list[DataPoint]:
        points = self._data.get((installation_id, metric), [])
        if since is not None:
            points = [p for p in points if p.timestamp >= since]
        if until is not None:
            points = [p for p in points if p.timestamp <= until]
        if label_filter:
            points = [
                p for p in points
                if all(p.labels.get(k) == v for k, v in label_filter.items())
            ]
        return points

    def _compute(self, agg: AggregationType, values: list[float]) -> float:
        if agg == AggregationType.SUM:
            return sum(values)
        if agg == AggregationType.AVG:
            return sum(values) / len(values)
        if agg == AggregationType.MIN:
            return min(values)
        if agg == AggregationType.MAX:
            return max(values)
        if agg == AggregationType.COUNT:
            return float(len(values))
        if agg == AggregationType.P99:
            sorted_vals = sorted(values)
            idx = int(math.ceil(0.99 * len(sorted_vals))) - 1
            return sorted_vals[max(0, idx)]
        return 0.0
