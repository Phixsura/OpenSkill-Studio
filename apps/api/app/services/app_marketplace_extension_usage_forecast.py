"""Usage Forecast — predict future extension usage based on historical data.

Uses simple trend analysis to forecast API calls, storage, and compute
usage, helping developers plan capacity and anticipate costs.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class UsageSample:
    period: str  # date or period label
    value: float


class UsageForecastService:
    """Forecasts extension usage based on historical trends."""

    def __init__(self):
        self._history: dict[str, dict[str, list[UsageSample]]] = {}

    def add_sample(self, extension_id: str, metric: str, sample: UsageSample) -> None:
        self._history.setdefault(extension_id, {}).setdefault(metric, []).append(sample)

    def get_trend(self, extension_id: str, metric: str) -> dict:
        """Calculate trend direction and growth rate."""
        samples = self._history.get(extension_id, {}).get(metric, [])
        if len(samples) < 2:
            return {"direction": "insufficient_data", "growth_rate": 0}

        values = [s.value for s in samples]
        first_half = sum(values[:len(values)//2]) / max(1, len(values)//2)
        second_half = sum(values[len(values)//2:]) / max(1, len(values) - len(values)//2)

        if first_half == 0:
            growth = 100.0 if second_half > 0 else 0
        else:
            growth = round((second_half - first_half) / first_half * 100, 1)

        direction = "growing" if growth > 5 else "declining" if growth < -5 else "stable"
        return {"direction": direction, "growth_rate": growth,
                "first_half_avg": round(first_half, 2), "second_half_avg": round(second_half, 2)}

    def forecast(self, extension_id: str, metric: str, periods_ahead: int = 7) -> list[dict]:
        """Forecast future values using linear projection."""
        samples = self._history.get(extension_id, {}).get(metric, [])
        if len(samples) < 3:
            return []

        values = [s.value for s in samples]
        n = len(values)
        # Simple linear regression
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n
        numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        slope = numerator / max(0.001, denominator)
        intercept = y_mean - slope * x_mean

        forecasts = []
        for i in range(periods_ahead):
            predicted = max(0, intercept + slope * (n + i))
            forecasts.append({
                "period_offset": i + 1,
                "predicted": round(predicted, 2),
                "confidence": max(0, round(100 - i * 10, 1)),  # decreasing confidence
            })
        return forecasts

    def estimate_cost(self, extension_id: str, cost_per_unit: float,
                      metric: str, periods: int = 30) -> dict:
        """Estimate future cost based on usage forecast."""
        forecasts = self.forecast(extension_id, metric, periods)
        if not forecasts:
            return {"estimated_cost": 0, "currency": "USD", "periods": 0}
        total_usage = sum(f["predicted"] for f in forecasts)
        return {
            "estimated_cost": round(total_usage * cost_per_unit, 2),
            "total_predicted_usage": round(total_usage, 2),
            "periods": len(forecasts),
            "avg_per_period": round(total_usage / len(forecasts), 2),
        }

    def detect_anomaly(self, extension_id: str, metric: str,
                       threshold_sigma: float = 2.0) -> dict:
        """Detect if the latest value is anomalous."""
        samples = self._history.get(extension_id, {}).get(metric, [])
        if len(samples) < 5:
            return {"anomaly": False, "reason": "insufficient_data"}

        values = [s.value for s in samples[:-1]]  # exclude latest
        latest = samples[-1].value
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std = variance ** 0.5

        if std == 0:
            is_anomaly = latest != mean
        else:
            z_score = abs(latest - mean) / std
            is_anomaly = z_score > threshold_sigma

        return {
            "anomaly": is_anomaly, "latest": latest,
            "mean": round(mean, 2), "std": round(std, 2),
            "direction": "spike" if latest > mean else "drop" if latest < mean else "normal",
        }
