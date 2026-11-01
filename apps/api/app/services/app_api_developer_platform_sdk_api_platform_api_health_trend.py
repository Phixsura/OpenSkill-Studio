"""App API Developer Platform API Health Trend — track health metrics over time."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class HealthDataPoint:
    timestamp: str  # ISO date
    uptime_pct: float
    error_rate_pct: float
    avg_latency_ms: float
    active_incidents: int

    @property
    def health_score(self) -> int:
        s = 100
        if self.uptime_pct < 99.9: s -= 25
        if self.error_rate_pct > 1: s -= 20
        if self.avg_latency_ms > 500: s -= 15
        if self.active_incidents > 0: s -= 20
        return max(0, s)

class AppAPIDeveloperPlatformSDKApiPlatformApiHealthTrend:
    def __init__(self) -> None:
        self._trends: dict[str, list[HealthDataPoint]] = {}

    def record(self, installation_id: str, timestamp: str, uptime_pct: float, error_rate_pct: float, avg_latency_ms: float, active_incidents: int = 0) -> HealthDataPoint:
        if not installation_id: raise ValueError("installation_id is required")
        dp = HealthDataPoint(timestamp=timestamp, uptime_pct=uptime_pct, error_rate_pct=error_rate_pct, avg_latency_ms=avg_latency_ms, active_incidents=active_incidents)
        self._trends.setdefault(installation_id, []).append(dp)
        return dp

    def trend(self, installation_id: str, limit: int = 30) -> list[HealthDataPoint]:
        return self._trends.get(installation_id, [])[-limit:]

    def latest_score(self, installation_id: str) -> int:
        points = self._trends.get(installation_id, [])
        return points[-1].health_score if points else 100

    def avg_score(self, installation_id: str) -> float:
        points = self._trends.get(installation_id, [])
        if not points: return 100.0
        return round(sum(p.health_score for p in points) / len(points), 1)
