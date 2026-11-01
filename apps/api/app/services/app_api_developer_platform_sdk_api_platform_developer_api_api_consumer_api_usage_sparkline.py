"""API Consumer Usage Sparkline — generate sparkline data for usage trends."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class SparklinePoint:
    label: str  # time bucket label
    value: int

@dataclass
class SparklineData:
    consumer_id: str
    metric: str  # "requests", "errors", "latency_avg"
    points: list[SparklinePoint] = field(default_factory=list)
    trend: str = "stable"  # "up", "down", "stable"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiUsageSparkline:
    def __init__(self) -> None:
        self._data: dict[tuple[str, str, str], list[SparklinePoint]] = {}

    def add_point(self, installation_id: str, consumer_id: str, metric: str, label: str, value: int) -> None:
        if not installation_id: raise ValueError("installation_id is required")
        if value < 0: raise ValueError("value must be non-negative")
        key = (installation_id, consumer_id, metric)
        self._data.setdefault(key, []).append(SparklinePoint(label=label, value=value))

    def get_sparkline(self, installation_id: str, consumer_id: str, metric: str, limit: int = 24) -> SparklineData:
        key = (installation_id, consumer_id, metric)
        points = self._data.get(key, [])[-limit:]
        trend = "stable"
        if len(points) >= 3:
            first_avg = sum(p.value for p in points[:len(points)//3]) / max(1, len(points)//3)
            last_avg = sum(p.value for p in points[-len(points)//3:]) / max(1, len(points)//3)
            if last_avg > first_avg * 1.1: trend = "up"
            elif last_avg < first_avg * 0.9: trend = "down"
        return SparklineData(consumer_id=consumer_id, metric=metric, points=points, trend=trend)

    def metrics_for_consumer(self, installation_id: str, consumer_id: str) -> list[str]:
        return list({m for (inst, cid, m) in self._data if inst == installation_id and cid == consumer_id})

    def consumer_count(self, installation_id: str) -> int:
        return len({cid for (inst, cid, _) in self._data if inst == installation_id})
