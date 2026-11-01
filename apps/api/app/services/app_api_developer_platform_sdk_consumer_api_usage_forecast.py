"""API Usage Forecast — time-series forecasting with trend projection."""
from __future__ import annotations

import statistics
import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class UsageDataPoint:
    period: str
    value: float


@dataclass
class UsageForecast:
    """Forecast API usage based on historical data with trend analysis."""

    _series: dict[str, list[UsageDataPoint]] = field(default_factory=dict)

    def add_data(self, metric_id: str, period: str, value: float) -> dict:
        if value < 0:
            raise ValueError("Value must be non-negative")
        self._series.setdefault(metric_id, []).append(UsageDataPoint(period, value))
        return {"metric_id": metric_id, "period": period, "data_points": len(self._series[metric_id])}

    def get_trend(self, metric_id: str) -> dict:
        points = self._series.get(metric_id, [])
        if len(points) < 2:
            return {"metric_id": metric_id, "trend": "insufficient_data"}
        values = [p.value for p in points]
        first_half = values[:len(values) // 2]
        second_half = values[len(values) // 2:]
        avg_first = statistics.mean(first_half)
        avg_second = statistics.mean(second_half)
        if avg_first == 0:
            growth_rate = 0.0
        else:
            growth_rate = (avg_second - avg_first) / avg_first
        if growth_rate > 0.05:
            direction = "increasing"
        elif growth_rate < -0.05:
            direction = "decreasing"
        else:
            direction = "stable"
        return {
            "metric_id": metric_id,
            "direction": direction,
            "growth_rate": round(growth_rate, 4),
            "avg_first_half": round(avg_first, 2),
            "avg_second_half": round(avg_second, 2),
            "data_points": len(values),
        }

    def forecast(self, metric_id: str, periods_ahead: int = 3) -> dict:
        points = self._series.get(metric_id, [])
        if len(points) < 2:
            return {"metric_id": metric_id, "error": "insufficient_data"}
        if periods_ahead < 1:
            raise ValueError("periods_ahead must be positive")
        values = [p.value for p in points]
        n = len(values)
        # Simple linear regression
        x_mean = (n - 1) / 2
        y_mean = statistics.mean(values)
        numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        slope = numerator / denominator if denominator != 0 else 0
        intercept = y_mean - slope * x_mean
        forecasted = []
        for i in range(periods_ahead):
            predicted = max(0, intercept + slope * (n + i))
            forecasted.append(round(predicted, 2))
        return {
            "metric_id": metric_id,
            "slope": round(slope, 4),
            "forecasted_values": forecasted,
            "periods_ahead": periods_ahead,
            "confidence": "high" if n >= 10 else "medium" if n >= 5 else "low",
        }

    def detect_anomalies(self, metric_id: str, threshold: float = 2.0) -> list[dict]:
        points = self._series.get(metric_id, [])
        if len(points) < 3:
            return []
        values = [p.value for p in points]
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)
        if stdev == 0:
            return []
        anomalies = []
        for p in points:
            z_score = (p.value - mean) / stdev
            if abs(z_score) > threshold:
                anomalies.append({
                    "period": p.period, "value": p.value,
                    "z_score": round(z_score, 2),
                    "type": "spike" if z_score > 0 else "dip",
                })
        return anomalies

    def get_summary(self, metric_id: str) -> dict:
        points = self._series.get(metric_id, [])
        if not points:
            return {"metric_id": metric_id, "status": "no_data"}
        values = [p.value for p in points]
        return {
            "metric_id": metric_id,
            "data_points": len(values),
            "min": min(values),
            "max": max(values),
            "mean": round(statistics.mean(values), 2),
            "latest": values[-1],
        }

    def list_metrics(self) -> list[str]:
        return sorted(self._series.keys())
