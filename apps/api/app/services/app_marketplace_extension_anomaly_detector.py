"""Anomaly Detector — statistical anomaly detection for metrics.

Implements:
- Z-score detection (how many stddevs from mean)
- IQR (Interquartile Range) method for outlier detection
- Moving average baseline with deviation tracking
- Seasonal awareness (hour-of-day patterns)
- Alert on anomaly with severity classification
"""
from __future__ import annotations
from dataclasses import dataclass, field
import statistics
import math
from collections import defaultdict


@dataclass
class AnomalyResult:
    value: float
    is_anomaly: bool
    method: str
    score: float  # z-score or IQR distance
    severity: str  # normal, warning, critical
    baseline: float
    threshold: float
    direction: str = ""  # high, low, normal


class AnomalyDetectorService:
    def __init__(self):
        self._series: dict[str, list[float]] = defaultdict(list)
        self._seasonal: dict[str, dict[int, list[float]]] = defaultdict(lambda: defaultdict(list))

    def add_point(self, metric: str, value: float, hour: int = -1) -> None:
        self._series[metric].append(value)
        if hour >= 0:
            self._seasonal[metric][hour].append(value)

    def add_points(self, metric: str, values: list[float]) -> None:
        self._series[metric].extend(values)

    def detect_zscore(self, metric: str, value: float,
                      threshold: float = 3.0) -> AnomalyResult:
        """Z-score: anomaly if |value - mean| > threshold * stddev."""
        data = self._series.get(metric, [])
        if len(data) < 10:
            return AnomalyResult(value, False, "zscore", 0, "normal", 0, threshold)

        mean = statistics.mean(data)
        stddev = statistics.stdev(data)
        if stddev == 0:
            return AnomalyResult(value, value != mean, "zscore",
                                 float('inf') if value != mean else 0,
                                 "critical" if value != mean else "normal",
                                 mean, threshold)

        z = abs(value - mean) / stddev
        is_anomaly = z > threshold
        direction = "high" if value > mean else "low" if value < mean else "normal"
        severity = "critical" if z > threshold * 1.5 else "warning" if z > threshold else "normal"

        return AnomalyResult(value, is_anomaly, "zscore", round(z, 3),
                             severity, round(mean, 2), threshold, direction)

    def detect_iqr(self, metric: str, value: float,
                   multiplier: float = 1.5) -> AnomalyResult:
        """IQR method: outlier if value outside [Q1 - k*IQR, Q3 + k*IQR]."""
        data = sorted(self._series.get(metric, []))
        if len(data) < 10:
            return AnomalyResult(value, False, "iqr", 0, "normal", 0, multiplier)

        n = len(data)
        q1 = data[n // 4]
        q3 = data[3 * n // 4]
        iqr = q3 - q1

        lower = q1 - multiplier * iqr
        upper = q3 + multiplier * iqr

        if value < lower:
            distance = (lower - value) / max(iqr, 0.001)
            return AnomalyResult(value, True, "iqr", round(distance, 3),
                                 "critical" if distance > 3 else "warning",
                                 round((q1 + q3) / 2, 2), multiplier, "low")
        if value > upper:
            distance = (value - upper) / max(iqr, 0.001)
            return AnomalyResult(value, True, "iqr", round(distance, 3),
                                 "critical" if distance > 3 else "warning",
                                 round((q1 + q3) / 2, 2), multiplier, "high")

        return AnomalyResult(value, False, "iqr", 0, "normal",
                             round((q1 + q3) / 2, 2), multiplier)

    def detect_seasonal(self, metric: str, value: float,
                        hour: int, threshold: float = 2.5) -> AnomalyResult:
        """Seasonal detection: compare against same hour-of-day baseline."""
        hourly_data = self._seasonal.get(metric, {}).get(hour, [])
        if len(hourly_data) < 5:
            return self.detect_zscore(metric, value, threshold)

        mean = statistics.mean(hourly_data)
        stddev = statistics.stdev(hourly_data) if len(hourly_data) > 1 else 0
        if stddev == 0:
            return AnomalyResult(value, value != mean, "seasonal", 0,
                                 "normal", mean, threshold)

        z = abs(value - mean) / stddev
        return AnomalyResult(value, z > threshold, "seasonal", round(z, 3),
                             "warning" if z > threshold else "normal",
                             round(mean, 2), threshold,
                             "high" if value > mean else "low")

    def detect_auto(self, metric: str, value: float,
                    hour: int = -1) -> AnomalyResult:
        """Auto-select best detection method."""
        if hour >= 0 and len(self._seasonal.get(metric, {}).get(hour, [])) >= 5:
            return self.detect_seasonal(metric, value, hour)

        data = self._series.get(metric, [])
        if len(data) >= 30:
            # Use IQR for skewed data, z-score for normal-ish
            sorted_d = sorted(data)
            q1 = sorted_d[len(data) // 4]
            q3 = sorted_d[3 * len(data) // 4]
            median = sorted_d[len(data) // 2]
            mean = statistics.mean(data)
            skew = abs(mean - median) / max(statistics.stdev(data), 0.001)
            if skew > 0.5:
                return self.detect_iqr(metric, value)

        return self.detect_zscore(metric, value)
