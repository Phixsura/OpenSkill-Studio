"""App API Developer Consumer Activity Heatmap — hourly activity patterns per consumer."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ActivityBucket:
    hour: int
    day_of_week: int
    count: int = 0

@dataclass
class ConsumerActivityMap:
    consumer_id: str
    buckets: dict[tuple[int, int], int] = field(default_factory=dict)

    @property
    def total_activity(self) -> int:
        return sum(self.buckets.values())

    @property
    def peak_hour(self) -> int:
        hourly = {}
        for (_, h), c in self.buckets.items():
            hourly[h] = hourly.get(h, 0) + c
        return max(hourly, key=hourly.get) if hourly else 0

    @property
    def peak_day(self) -> int:
        daily = {}
        for (d, _), c in self.buckets.items():
            daily[d] = daily.get(d, 0) + c
        return max(daily, key=daily.get) if daily else 0

class AppAPIDeveloperPlatformSDKApiDeveloperApiApiConsumerActivityHeatmap:
    def __init__(self) -> None:
        self._maps: dict[tuple[str, str], ConsumerActivityMap] = {}

    def record(self, installation_id: str, consumer_id: str, day_of_week: int, hour: int, count: int = 1) -> ConsumerActivityMap:
        if not installation_id: raise ValueError("installation_id is required")
        if not 0 <= day_of_week <= 6: raise ValueError("day must be 0-6")
        if not 0 <= hour <= 23: raise ValueError("hour must be 0-23")
        key = (installation_id, consumer_id)
        if key not in self._maps:
            self._maps[key] = ConsumerActivityMap(consumer_id=consumer_id)
        m = self._maps[key]
        bk = (day_of_week, hour)
        m.buckets[bk] = m.buckets.get(bk, 0) + count
        return m

    def get(self, installation_id: str, consumer_id: str) -> ConsumerActivityMap | None:
        return self._maps.get((installation_id, consumer_id))

    def most_active(self, installation_id: str, limit: int = 5) -> list[ConsumerActivityMap]:
        maps = [m for (inst, _), m in self._maps.items() if inst == installation_id]
        return sorted(maps, key=lambda m: m.total_activity, reverse=True)[:limit]

    def all_maps(self, installation_id: str) -> list[ConsumerActivityMap]:
        return [m for (inst, _), m in self._maps.items() if inst == installation_id]
