"""App API Developer Endpoint Usage Trend — track daily/weekly endpoint usage trends."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class DailyUsage:
    date: str  # YYYY-MM-DD
    count: int

@dataclass
class EndpointTrend:
    endpoint: str
    daily_usage: list[DailyUsage] = field(default_factory=list)

    @property
    def total(self) -> int:
        return sum(d.count for d in self.daily_usage)

    @property
    def avg_daily(self) -> float:
        return round(self.total / len(self.daily_usage), 1) if self.daily_usage else 0.0

    @property
    def trend_direction(self) -> str:
        if len(self.daily_usage) < 3: return "unknown"
        recent = sum(d.count for d in self.daily_usage[-3:]) / 3
        earlier = sum(d.count for d in self.daily_usage[:3]) / 3
        if earlier == 0: return "growing" if recent > 0 else "stable"
        change = (recent - earlier) / earlier * 100
        if change > 10: return "growing"
        if change < -10: return "declining"
        return "stable"

class AppAPIDeveloperAPIApiEndpointUsageTrend:
    def __init__(self) -> None:
        self._trends: dict[tuple[str, str], EndpointTrend] = {}

    def record(self, installation_id: str, endpoint: str, date: str, count: int) -> EndpointTrend:
        if not installation_id: raise ValueError("installation_id is required")
        if count < 0: raise ValueError("count must be non-negative")
        key = (installation_id, endpoint)
        if key not in self._trends:
            self._trends[key] = EndpointTrend(endpoint=endpoint)
        t = self._trends[key]
        t.daily_usage.append(DailyUsage(date=date, count=count))
        return t

    def get_trend(self, installation_id: str, endpoint: str) -> EndpointTrend | None:
        return self._trends.get((installation_id, endpoint))

    def growing_endpoints(self, installation_id: str) -> list[EndpointTrend]:
        return [t for (inst, _), t in self._trends.items() if inst == installation_id and t.trend_direction == "growing"]

    def declining_endpoints(self, installation_id: str) -> list[EndpointTrend]:
        return [t for (inst, _), t in self._trends.items() if inst == installation_id and t.trend_direction == "declining"]

    def all_trends(self, installation_id: str) -> list[EndpointTrend]:
        return [t for (inst, _), t in self._trends.items() if inst == installation_id]
