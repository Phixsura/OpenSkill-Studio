"""Consumer API Analytics — aggregated analytics per consumer."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class AnalyticsDataPoint:
    timestamp: datetime
    metric: str
    value: float
    dimensions: dict[str, str] = field(default_factory=dict)

@dataclass
class AnalyticsSummary:
    metric: str
    total: float
    average: float
    min_value: float
    max_value: float
    data_points: int
    trend: str  # "up", "down", "flat"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiAnalytics:
    def __init__(self) -> None:
        self._data: dict[tuple[str, str], list[AnalyticsDataPoint]] = {}

    def record(self, installation_id: str, consumer_id: str, point: AnalyticsDataPoint) -> AnalyticsDataPoint:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, consumer_id)
        if key not in self._data:
            self._data[key] = []
        self._data[key].append(point)
        return point

    def summarize(self, installation_id: str, consumer_id: str, metric: str) -> AnalyticsSummary:
        points = [p for p in self._data.get((installation_id, consumer_id), []) if p.metric == metric]
        if not points:
            return AnalyticsSummary(metric=metric, total=0, average=0, min_value=0, max_value=0, data_points=0, trend="flat")
        values = [p.value for p in points]
        total = sum(values)
        avg = total / len(values)
        # Trend: compare first half vs second half
        mid = len(values) // 2
        if mid > 0:
            first_avg = sum(values[:mid]) / mid
            second_avg = sum(values[mid:]) / (len(values) - mid)
            if second_avg > first_avg * 1.05:
                trend = "up"
            elif second_avg < first_avg * 0.95:
                trend = "down"
            else:
                trend = "flat"
        else:
            trend = "flat"
        return AnalyticsSummary(metric=metric, total=round(total, 2), average=round(avg, 2), min_value=min(values), max_value=max(values), data_points=len(values), trend=trend)

    def top_dimensions(self, installation_id: str, consumer_id: str, metric: str, dimension: str, limit: int = 5) -> list[tuple[str, float]]:
        points = [p for p in self._data.get((installation_id, consumer_id), []) if p.metric == metric and dimension in p.dimensions]
        groups: dict[str, float] = {}
        for p in points:
            dim_val = p.dimensions[dimension]
            groups[dim_val] = groups.get(dim_val, 0) + p.value
        return sorted(groups.items(), key=lambda x: -x[1])[:limit]

    def get_metrics(self, installation_id: str, consumer_id: str) -> list[str]:
        points = self._data.get((installation_id, consumer_id), [])
        return sorted(set(p.metric for p in points))
