"""API Consumer Usage Forecast — predict future API usage from historical data."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class UsageSample:
    period: str  # "2024-01", "2024-02", etc.
    request_count: int

@dataclass
class Forecast:
    consumer_id: str
    next_period: str
    predicted_requests: int
    growth_rate_pct: float
    confidence: str  # "high", "medium", "low"
    trend: str  # "growing", "stable", "declining"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerApiUsageForecast:
    def __init__(self) -> None:
        self._history: dict[tuple[str, str], list[UsageSample]] = {}

    def add_samples(self, installation_id: str, consumer_id: str, samples: list[UsageSample]) -> int:
        if not installation_id: raise ValueError("installation_id is required")
        if not samples: raise ValueError("At least one sample required")
        key = (installation_id, consumer_id)
        self._history.setdefault(key, []).extend(samples)
        return len(self._history[key])

    def forecast(self, installation_id: str, consumer_id: str, next_period: str) -> Forecast:
        samples = self._history.get((installation_id, consumer_id), [])
        if len(samples) < 2: raise ValueError("Need at least 2 samples for forecast")
        counts = [s.request_count for s in samples]
        recent = counts[-3:] if len(counts) >= 3 else counts
        avg_recent = sum(recent) / len(recent)
        older = counts[:-len(recent)] if len(counts) > len(recent) else counts[:1]
        avg_older = sum(older) / len(older)
        growth = ((avg_recent - avg_older) / max(1, avg_older)) * 100 if avg_older > 0 else 0
        predicted = int(avg_recent * (1 + growth / 100))
        predicted = max(0, predicted)
        trend = "growing" if growth > 5 else "declining" if growth < -5 else "stable"
        confidence = "high" if len(samples) >= 6 else "medium" if len(samples) >= 3 else "low"
        return Forecast(consumer_id=consumer_id, next_period=next_period, predicted_requests=predicted, growth_rate_pct=round(growth, 1), confidence=confidence, trend=trend)

    def get_history(self, installation_id: str, consumer_id: str) -> list[UsageSample]:
        return self._history.get((installation_id, consumer_id), [])

    def consumer_count(self, installation_id: str) -> int:
        return len({cid for (inst, cid) in self._history if inst == installation_id})
