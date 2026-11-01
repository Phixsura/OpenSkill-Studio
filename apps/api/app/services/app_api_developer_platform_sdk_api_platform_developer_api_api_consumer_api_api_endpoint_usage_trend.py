"""API Consumer Endpoint Usage Trend — track per-endpoint usage trends over time."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class UsageTrendPoint:
    period: str
    request_count: int

@dataclass
class EndpointTrend:
    endpoint: str
    method: str
    points: list[UsageTrendPoint] = field(default_factory=list)

    @property
    def trend_direction(self) -> str:
        if len(self.points) < 2: return "stable"
        recent = [p.request_count for p in self.points[-3:]]
        older = [p.request_count for p in self.points[:max(1, len(self.points) // 2)]]
        avg_recent = sum(recent) / len(recent) if recent else 0
        avg_older = sum(older) / len(older) if older else 0
        if avg_older == 0: return "stable"
        change = (avg_recent - avg_older) / avg_older * 100
        if change > 15: return "growing"
        if change < -15: return "declining"
        return "stable"

    @property
    def total_requests(self) -> int:
        return sum(p.request_count for p in self.points)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointUsageTrend:
    def __init__(self) -> None:
        self._trends: dict[tuple[str, str, str], EndpointTrend] = {}

    def record(self, installation_id: str, endpoint: str, method: str, period: str, count: int) -> EndpointTrend:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, method.upper(), endpoint)
        trend = self._trends.get(key)
        if trend is None:
            trend = EndpointTrend(endpoint=endpoint, method=method.upper())
            self._trends[key] = trend
        existing = next((p for p in trend.points if p.period == period), None)
        if existing: existing.request_count += count
        else: trend.points.append(UsageTrendPoint(period=period, request_count=count))
        return trend

    def growing_endpoints(self, installation_id: str) -> list[EndpointTrend]:
        return [t for (inst, _, _), t in self._trends.items() if inst == installation_id and t.trend_direction == "growing"]

    def declining_endpoints(self, installation_id: str) -> list[EndpointTrend]:
        return [t for (inst, _, _), t in self._trends.items() if inst == installation_id and t.trend_direction == "declining"]

    def list_trends(self, installation_id: str) -> list[EndpointTrend]:
        return [t for (inst, _, _), t in self._trends.items() if inst == installation_id]
