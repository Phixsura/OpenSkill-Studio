"""Consumer Usage Forecast — predict future API usage based on historical patterns."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class UsageDataPoint:
    period: str   # e.g. "2026-01", "2026-02"
    requests: int
    errors: int = 0

@dataclass
class ForecastResult:
    next_period: str
    predicted_requests: int
    confidence: float  # 0.0-1.0
    trend: str  # "increasing", "stable", "decreasing"
    growth_rate: float  # percentage

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerUsageForecast:
    def __init__(self) -> None:
        self._history: dict[tuple[str, str], list[UsageDataPoint]] = {}

    def add_data(self, installation_id: str, consumer_id: str, point: UsageDataPoint) -> UsageDataPoint:
        if not installation_id:
            raise ValueError("installation_id is required")
        if point.requests < 0:
            raise ValueError("requests must be non-negative")
        key = (installation_id, consumer_id)
        if key not in self._history:
            self._history[key] = []
        self._history[key].append(point)
        self._history[key].sort(key=lambda p: p.period)
        return point

    def forecast(self, installation_id: str, consumer_id: str, next_period: str) -> ForecastResult:
        history = self._history.get((installation_id, consumer_id), [])
        if len(history) < 2:
            avg = history[0].requests if history else 0
            return ForecastResult(next_period=next_period, predicted_requests=avg, confidence=0.3, trend="stable", growth_rate=0.0)
        # Simple linear trend
        values = [p.requests for p in history]
        n = len(values)
        avg_x = (n - 1) / 2.0
        avg_y = sum(values) / n
        num = sum((i - avg_x) * (v - avg_y) for i, v in enumerate(values))
        den = sum((i - avg_x) ** 2 for i in range(n))
        slope = num / den if den != 0 else 0
        intercept = avg_y - slope * avg_x
        predicted = max(0, int(slope * n + intercept))
        # Trend
        growth = ((values[-1] - values[0]) / values[0] * 100) if values[0] > 0 else 0.0
        if growth > 5:
            trend = "increasing"
        elif growth < -5:
            trend = "decreasing"
        else:
            trend = "stable"
        # Confidence based on data points and variance
        variance = sum((v - avg_y) ** 2 for v in values) / n
        cv = (variance ** 0.5) / avg_y if avg_y > 0 else 1.0
        confidence = min(0.95, max(0.1, 1.0 - cv) * min(1.0, n / 6))
        return ForecastResult(next_period=next_period, predicted_requests=predicted, confidence=round(confidence, 2), trend=trend, growth_rate=round(growth, 1))

    def get_history(self, installation_id: str, consumer_id: str) -> list[UsageDataPoint]:
        return self._history.get((installation_id, consumer_id), [])
