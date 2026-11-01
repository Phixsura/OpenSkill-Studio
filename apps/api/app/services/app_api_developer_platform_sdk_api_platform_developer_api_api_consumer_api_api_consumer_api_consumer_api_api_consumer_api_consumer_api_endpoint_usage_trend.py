"""Consumer API Endpoint Usage Trend — track usage trends over time per endpoint."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class UsagePeriod:
    period: str  # "2026-06-01", "2026-W22", "2026-06"
    request_count: int
    error_count: int
    avg_latency_ms: float

@dataclass
class UsageTrend:
    endpoint_path: str
    periods: list[UsagePeriod] = field(default_factory=list)
    trend_direction: str = "stable"  # "growing", "declining", "stable", "volatile"
    growth_rate_pct: float = 0.0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiEndpointUsageTrend:
    def __init__(self) -> None:
        self._trends: dict[tuple[str, str], list[UsagePeriod]] = {}

    def record_period(self, installation_id: str, endpoint_path: str, period: UsagePeriod) -> UsagePeriod:
        if not installation_id:
            raise ValueError("installation_id is required")
        if period.request_count < 0:
            raise ValueError("request_count must be non-negative")
        key = (installation_id, endpoint_path)
        if key not in self._trends:
            self._trends[key] = []
        self._trends[key].append(period)
        self._trends[key].sort(key=lambda p: p.period)
        return period

    def get_trend(self, installation_id: str, endpoint_path: str) -> UsageTrend:
        periods = self._trends.get((installation_id, endpoint_path), [])
        if len(periods) < 2:
            return UsageTrend(endpoint_path=endpoint_path, periods=periods, trend_direction="stable", growth_rate_pct=0)
        values = [p.request_count for p in periods]
        first_half = sum(values[:len(values)//2]) / max(len(values)//2, 1)
        second_half = sum(values[len(values)//2:]) / max(len(values) - len(values)//2, 1)
        if first_half > 0:
            growth = ((second_half - first_half) / first_half) * 100
        else:
            growth = 0
        # Volatility check
        avg = sum(values) / len(values)
        variance = sum((v - avg) ** 2 for v in values) / len(values)
        cv = (variance ** 0.5) / max(avg, 1)
        if cv > 0.5:
            direction = "volatile"
        elif growth > 10:
            direction = "growing"
        elif growth < -10:
            direction = "declining"
        else:
            direction = "stable"
        return UsageTrend(endpoint_path=endpoint_path, periods=periods, trend_direction=direction, growth_rate_pct=round(growth, 1))

    def list_endpoints(self, installation_id: str) -> list[str]:
        return sorted({ep for (inst, ep) in self._trends if inst == installation_id})
