"""App API Developer API Usage Heatmap — hourly usage patterns visualization."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class HourlyBucket:
    day_of_week: int  # 0=Mon, 6=Sun
    hour: int  # 0-23
    request_count: int = 0
    error_count: int = 0

class AppAPIDeveloperAPIApiUsageHeatmap:
    def __init__(self) -> None:
        self._buckets: dict[str, dict[tuple[int, int], HourlyBucket]] = {}

    def record(self, installation_id: str, day_of_week: int, hour: int, success: bool = True) -> HourlyBucket:
        if not installation_id: raise ValueError("installation_id is required")
        if not 0 <= day_of_week <= 6: raise ValueError("day_of_week must be 0-6")
        if not 0 <= hour <= 23: raise ValueError("hour must be 0-23")
        buckets = self._buckets.setdefault(installation_id, {})
        key = (day_of_week, hour)
        if key not in buckets:
            buckets[key] = HourlyBucket(day_of_week=day_of_week, hour=hour)
        b = buckets[key]
        b.request_count += 1
        if not success: b.error_count += 1
        return b

    def heatmap(self, installation_id: str) -> list[HourlyBucket]:
        return sorted(self._buckets.get(installation_id, {}).values(), key=lambda b: (b.day_of_week, b.hour))

    def peak_hour(self, installation_id: str) -> HourlyBucket | None:
        buckets = list(self._buckets.get(installation_id, {}).values())
        return max(buckets, key=lambda b: b.request_count) if buckets else None

    def total_requests(self, installation_id: str) -> int:
        return sum(b.request_count for b in self._buckets.get(installation_id, {}).values())
