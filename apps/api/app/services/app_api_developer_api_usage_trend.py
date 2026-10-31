"""App API Developer API Usage Trend — track usage trends over time."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class UsageDataPoint:
    period: str
    requests: int
    errors: int

    @property
    def error_rate(self) -> float:
        if self.requests == 0: return 0.0
        return round(self.errors / self.requests * 100, 1)

class AppAPIDeveloperAPIUsageTrend:
    def __init__(self) -> None:
        self._data: dict[str, list[UsageDataPoint]] = {}

    def add_point(self, installation_id: str, period: str, requests: int, errors: int) -> UsageDataPoint:
        if not installation_id: raise ValueError("installation_id is required")
        if requests < 0: raise ValueError("requests must be non-negative")
        dp = UsageDataPoint(period=period, requests=requests, errors=errors)
        self._data.setdefault(installation_id, []).append(dp)
        return dp

    def trend(self, installation_id: str, limit: int = 12) -> list[UsageDataPoint]:
        return self._data.get(installation_id, [])[-limit:]

    def growth_rate(self, installation_id: str) -> float:
        points = self._data.get(installation_id, [])
        if len(points) < 2: return 0.0
        prev, curr = points[-2].requests, points[-1].requests
        if prev == 0: return 0.0
        return round((curr - prev) / prev * 100, 1)
