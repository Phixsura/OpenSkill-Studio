"""App Usage Forecast — predict future usage based on historical trends.

Forecasts usage metrics for installed apps:
- Linear regression on historical data points
- Predict usage at future timestamps
- Days until quota exhaustion
- Trend detection (growing, stable, declining)
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class ForecastResult:
    """Result of a usage forecast."""

    metric: str
    current: float
    predicted: float
    trend: str  # "growing", "stable", "declining"
    days_to_limit: float | None  # None if not approaching limit
    growth_rate_per_day: float


class AppUsageForecast:
    """Predict future usage based on historical trends."""

    def __init__(self) -> None:
        # (installation_id, metric) → list[(timestamp, value)]
        self._data: dict[tuple[str, str], list[tuple[float, float]]] = {}

    def record(
        self, installation_id: str, metric: str, value: float, timestamp: float
    ) -> None:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not metric:
            raise ValueError("metric is required")
        key = (installation_id, metric)
        self._data.setdefault(key, []).append((timestamp, value))

    def forecast(
        self,
        installation_id: str,
        metric: str,
        future_timestamp: float,
        limit: float | None = None,
    ) -> ForecastResult:
        """Forecast usage at a future timestamp."""
        key = (installation_id, metric)
        points = self._data.get(key, [])
        if len(points) < 2:
            raise ValueError("Need at least 2 data points for forecast")

        # Simple linear regression
        slope, intercept = self._linear_fit(points)
        current = points[-1][1]
        predicted = max(0, slope * future_timestamp + intercept)

        # Growth rate per day (86400 seconds)
        growth_per_day = slope * 86400

        # Trend
        if abs(growth_per_day) < current * 0.001:  # < 0.1% per day
            trend = "stable"
        elif growth_per_day > 0:
            trend = "growing"
        else:
            trend = "declining"

        # Days to limit
        days_to_limit = None
        if limit is not None and slope > 0 and current < limit:
            remaining = limit - current
            days_to_limit = round(remaining / growth_per_day, 1) if growth_per_day > 0 else None

        return ForecastResult(
            metric=metric, current=round(current, 2),
            predicted=round(predicted, 2), trend=trend,
            days_to_limit=days_to_limit,
            growth_rate_per_day=round(growth_per_day, 4),
        )

    def _linear_fit(self, points: list[tuple[float, float]]) -> tuple[float, float]:
        """Simple linear regression. Returns (slope, intercept)."""
        n = len(points)
        sum_x = sum(p[0] for p in points)
        sum_y = sum(p[1] for p in points)
        sum_xy = sum(p[0] * p[1] for p in points)
        sum_x2 = sum(p[0] ** 2 for p in points)

        denom = n * sum_x2 - sum_x ** 2
        if denom == 0:
            return 0.0, sum_y / n

        slope = (n * sum_xy - sum_x * sum_y) / denom
        intercept = (sum_y - slope * sum_x) / n
        return slope, intercept
