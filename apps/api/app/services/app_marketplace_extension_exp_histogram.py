"""Exponential Histogram — streaming quantile estimation with log-space buckets.

Used by OpenTelemetry and Prometheus for histogram metrics.

Implements:
- Exponential bucket boundaries (geometric progression)
- Streaming insert (O(1) per data point)
- Approximate quantile queries (p50, p90, p99)
- Merge two histograms (from different time windows or nodes)
- Summary statistics (count, sum, min, max, mean)
"""
from __future__ import annotations
from dataclasses import dataclass, field
import math


class ExponentialHistogramService:
    def __init__(self, base: float = 2.0, num_buckets: int = 32,
                 min_value: float = 1.0):
        """Buckets: [min*base^0, min*base^1), [min*base^1, min*base^2), ..."""
        self._base = base
        self._num_buckets = num_buckets
        self._min_value = min_value
        self._buckets: list[int] = [0] * num_buckets
        self._boundaries: list[float] = [
            min_value * (base ** i) for i in range(num_buckets + 1)]
        self._count = 0
        self._sum = 0.0
        self._min = float('inf')
        self._max = float('-inf')
        self._underflow = 0  # below min_value
        self._overflow = 0   # above max bucket

    def observe(self, value: float) -> int:
        """Record a value. Returns bucket index."""
        self._count += 1
        self._sum += value
        self._min = min(self._min, value)
        self._max = max(self._max, value)

        if value < self._min_value:
            self._underflow += 1
            return -1

        # Find bucket: log_base(value / min_value)
        idx = int(math.log(value / self._min_value) / math.log(self._base))
        if idx >= self._num_buckets:
            self._overflow += 1
            return self._num_buckets
        self._buckets[idx] += 1
        return idx

    def observe_many(self, values: list[float]) -> None:
        for v in values:
            self.observe(v)

    def quantile(self, q: float) -> float:
        """Estimate the q-th quantile (0.0 to 1.0)."""
        if self._count == 0:
            return 0.0

        target = q * self._count
        cumulative = self._underflow

        for i, count in enumerate(self._buckets):
            cumulative += count
            if cumulative >= target:
                # Interpolate within bucket
                lower = self._boundaries[i]
                upper = self._boundaries[i + 1] if i + 1 < len(self._boundaries) else lower * self._base
                fraction = (target - (cumulative - count)) / max(1, count)
                return lower + fraction * (upper - lower)

        return self._max

    @property
    def p50(self) -> float: return self.quantile(0.5)
    @property
    def p90(self) -> float: return self.quantile(0.9)
    @property
    def p95(self) -> float: return self.quantile(0.95)
    @property
    def p99(self) -> float: return self.quantile(0.99)

    @property
    def mean(self) -> float:
        return round(self._sum / self._count, 4) if self._count else 0

    def merge(self, other: ExponentialHistogramService) -> ExponentialHistogramService:
        """Merge two histograms (e.g., from different nodes)."""
        if self._num_buckets != other._num_buckets:
            raise ValueError("Histograms must have same bucket count")
        result = ExponentialHistogramService(self._base, self._num_buckets, self._min_value)
        for i in range(self._num_buckets):
            result._buckets[i] = self._buckets[i] + other._buckets[i]
        result._count = self._count + other._count
        result._sum = self._sum + other._sum
        result._min = min(self._min, other._min)
        result._max = max(self._max, other._max)
        result._underflow = self._underflow + other._underflow
        result._overflow = self._overflow + other._overflow
        return result

    def get_buckets(self) -> list[dict]:
        return [{"lower": self._boundaries[i],
                 "upper": self._boundaries[i + 1] if i + 1 < len(self._boundaries) else float('inf'),
                 "count": self._buckets[i]}
                for i in range(self._num_buckets) if self._buckets[i] > 0]

    def stats(self) -> dict:
        return {
            "count": self._count, "sum": round(self._sum, 2),
            "min": self._min if self._count else 0,
            "max": self._max if self._count else 0,
            "mean": self.mean,
            "p50": round(self.p50, 2), "p90": round(self.p90, 2),
            "p95": round(self.p95, 2), "p99": round(self.p99, 2),
            "underflow": self._underflow, "overflow": self._overflow,
        }
