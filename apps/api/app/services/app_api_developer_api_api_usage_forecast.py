"""App API Developer API Usage Forecast — predict future API usage trends."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class UsageForecast:
    endpoint: str
    current_daily_avg: float
    trend: str  # "growing", "stable", "declining"
    growth_rate_pct: float
    forecast_7d: float
    forecast_30d: float

class AppAPIDeveloperAPIApiUsageForecast:
    def __init__(self) -> None:
        self._samples: dict[tuple[str, str], list[float]] = {}

    def add_daily_sample(self, installation_id: str, endpoint: str, count: float) -> None:
        if not installation_id: raise ValueError("installation_id is required")
        if count < 0: raise ValueError("count must be non-negative")
        self._samples.setdefault((installation_id, endpoint), []).append(count)

    def forecast(self, installation_id: str, endpoint: str) -> UsageForecast:
        key = (installation_id, endpoint)
        samples = self._samples.get(key, [])
        if len(samples) < 3: raise ValueError("Need at least 3 daily samples")
        avg = sum(samples) / len(samples)
        recent = sum(samples[-3:]) / 3
        earlier = sum(samples[:3]) / 3 if len(samples) >= 6 else avg
        growth = round((recent - earlier) / earlier * 100, 1) if earlier > 0 else 0.0
        trend = "growing" if growth > 5 else "declining" if growth < -5 else "stable"
        daily_growth = growth / 100 / max(len(samples), 1)
        f7 = round(recent * (1 + daily_growth * 7), 0)
        f30 = round(recent * (1 + daily_growth * 30), 0)
        return UsageForecast(endpoint=endpoint, current_daily_avg=round(avg, 1), trend=trend, growth_rate_pct=growth, forecast_7d=f7, forecast_30d=f30)

    def all_forecasts(self, installation_id: str) -> list[UsageForecast]:
        endpoints = set(ep for (inst, ep) in self._samples if inst == installation_id)
        results = []
        for ep in sorted(endpoints):
            try:
                results.append(self.forecast(installation_id, ep))
            except ValueError:
                pass
        return results

    def growing_endpoints(self, installation_id: str) -> list[UsageForecast]:
        return [f for f in self.all_forecasts(installation_id) if f.trend == "growing"]
