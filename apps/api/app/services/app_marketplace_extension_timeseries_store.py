"""Time-Series Store — efficient storage and querying of timestamped metrics.

Implements:
- Append-only time-series data per metric
- Time range queries with resolution
- Aggregation functions: avg, min, max, sum, count, p99
- Automatic downsampling for older data
- Rate-of-change calculation
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import statistics
import math


@dataclass
class DataPoint:
    timestamp: float
    value: float


class TimeSeriesStoreService:
    def __init__(self, max_points_per_metric: int = 100000):
        self._series: dict[str, list[DataPoint]] = {}
        self._max_points = max_points_per_metric

    def record(self, metric: str, value: float,
               timestamp: float | None = None) -> DataPoint:
        ts = timestamp or time.time()
        dp = DataPoint(timestamp=ts, value=value)
        if metric not in self._series:
            self._series[metric] = []
        self._series[metric].append(dp)
        # Evict oldest if over limit
        if len(self._series[metric]) > self._max_points:
            self._series[metric] = self._series[metric][-self._max_points:]
        return dp

    def query(self, metric: str, start: float, end: float) -> list[DataPoint]:
        """Query raw data points in a time range."""
        points = self._series.get(metric, [])
        return [p for p in points if start <= p.timestamp <= end]

    def aggregate(self, metric: str, start: float, end: float,
                  func: str = "avg", bucket_seconds: float = 60) -> list[dict]:
        """Aggregate data into time buckets."""
        points = self.query(metric, start, end)
        if not points:
            return []

        # Group into buckets
        buckets: dict[int, list[float]] = {}
        for p in points:
            bucket_key = int(p.timestamp // bucket_seconds)
            if bucket_key not in buckets:
                buckets[bucket_key] = []
            buckets[bucket_key].append(p.value)

        result = []
        for bucket_key in sorted(buckets):
            values = buckets[bucket_key]
            ts = bucket_key * bucket_seconds
            agg_value = self._calc_aggregate(values, func)
            result.append({"timestamp": ts, "value": round(agg_value, 4),
                           "count": len(values)})
        return result

    def _calc_aggregate(self, values: list[float], func: str) -> float:
        if not values:
            return 0.0
        if func == "avg":
            return statistics.mean(values)
        elif func == "sum":
            return sum(values)
        elif func == "min":
            return min(values)
        elif func == "max":
            return max(values)
        elif func == "count":
            return float(len(values))
        elif func == "p99":
            sorted_v = sorted(values)
            idx = int(len(sorted_v) * 0.99)
            return sorted_v[min(idx, len(sorted_v) - 1)]
        elif func == "stddev":
            return statistics.stdev(values) if len(values) > 1 else 0.0
        return statistics.mean(values)

    def rate(self, metric: str, start: float, end: float) -> float:
        """Calculate rate of change (per second) over a time range."""
        points = self.query(metric, start, end)
        if len(points) < 2:
            return 0.0
        first, last = points[0], points[-1]
        duration = last.timestamp - first.timestamp
        if duration <= 0:
            return 0.0
        return round((last.value - first.value) / duration, 4)

    def downsample(self, metric: str, older_than: float,
                   bucket_seconds: float = 300) -> int:
        """Downsample old data: replace raw points with averages."""
        points = self._series.get(metric, [])
        cutoff = time.time() - older_than
        old_points = [p for p in points if p.timestamp < cutoff]
        new_points = [p for p in points if p.timestamp >= cutoff]

        if not old_points:
            return 0

        # Aggregate old points into buckets
        buckets: dict[int, list[DataPoint]] = {}
        for p in old_points:
            key = int(p.timestamp // bucket_seconds)
            if key not in buckets:
                buckets[key] = []
            buckets[key].append(p)

        downsampled = []
        for key in sorted(buckets):
            bucket_points = buckets[key]
            avg_value = statistics.mean(p.value for p in bucket_points)
            avg_ts = statistics.mean(p.timestamp for p in bucket_points)
            downsampled.append(DataPoint(timestamp=avg_ts, value=round(avg_value, 4)))

        removed = len(old_points) - len(downsampled)
        self._series[metric] = downsampled + new_points
        return removed

    def get_latest(self, metric: str) -> DataPoint | None:
        points = self._series.get(metric, [])
        return points[-1] if points else None

    def list_metrics(self) -> list[str]:
        return sorted(self._series.keys())
