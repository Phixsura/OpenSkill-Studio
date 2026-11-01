"""Consumer API Usage Heatmap — visualize API usage patterns by time and endpoint."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class UsageBucket:
    hour: int  # 0-23
    day_of_week: int  # 0=Monday, 6=Sunday
    request_count: int = 0
    error_count: int = 0
    avg_latency_ms: float = 0.0

@dataclass
class HeatmapData:
    consumer_id: str
    buckets: list[UsageBucket] = field(default_factory=list)
    peak_hour: int = 0
    peak_day: int = 0
    total_requests: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiUsageHeatmap:
    def __init__(self) -> None:
        self._data: dict[tuple[str, str], dict[tuple[int, int], UsageBucket]] = {}

    def record(self, installation_id: str, consumer_id: str, timestamp: datetime, latency_ms: float = 0, is_error: bool = False) -> None:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, consumer_id)
        if key not in self._data:
            self._data[key] = {}
        hour = timestamp.hour
        dow = timestamp.weekday()
        bkey = (hour, dow)
        bucket = self._data[key].get(bkey)
        if not bucket:
            bucket = UsageBucket(hour=hour, day_of_week=dow)
            self._data[key][bkey] = bucket
        bucket.request_count += 1
        if is_error:
            bucket.error_count += 1
        # Running average
        n = bucket.request_count
        bucket.avg_latency_ms = bucket.avg_latency_ms + (latency_ms - bucket.avg_latency_ms) / n

    def get_heatmap(self, installation_id: str, consumer_id: str) -> HeatmapData:
        key = (installation_id, consumer_id)
        buckets_map = self._data.get(key, {})
        if not buckets_map:
            return HeatmapData(consumer_id=consumer_id)
        buckets = list(buckets_map.values())
        total = sum(b.request_count for b in buckets)
        peak = max(buckets, key=lambda b: b.request_count)
        return HeatmapData(consumer_id=consumer_id, buckets=buckets, peak_hour=peak.hour, peak_day=peak.day_of_week, total_requests=total)

    def get_peak_hours(self, installation_id: str, consumer_id: str, top_n: int = 5) -> list[UsageBucket]:
        key = (installation_id, consumer_id)
        buckets = list(self._data.get(key, {}).values())
        return sorted(buckets, key=lambda b: -b.request_count)[:top_n]
