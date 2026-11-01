"""App API Developer Consumer Usage Trend — per-consumer usage trend analysis."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ConsumerTrend:
    consumer_id: str
    daily_counts: list[int] = field(default_factory=list)

    @property
    def total(self) -> int:
        return sum(self.daily_counts)

    @property
    def avg_daily(self) -> float:
        return round(self.total / len(self.daily_counts), 1) if self.daily_counts else 0.0

    @property
    def trend(self) -> str:
        if len(self.daily_counts) < 4: return "unknown"
        mid = len(self.daily_counts) // 2
        first_half = sum(self.daily_counts[:mid]) / max(mid, 1)
        second_half = sum(self.daily_counts[mid:]) / max(len(self.daily_counts) - mid, 1)
        if first_half == 0: return "growing" if second_half > 0 else "stable"
        change = (second_half - first_half) / first_half * 100
        if change > 15: return "growing"
        if change < -15: return "declining"
        return "stable"

class AppAPIDeveloperAPIApiDeveloperApiApiConsumerUsageTrend:
    def __init__(self) -> None:
        self._trends: dict[tuple[str, str], ConsumerTrend] = {}

    def add_daily(self, installation_id: str, consumer_id: str, count: int) -> ConsumerTrend:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, consumer_id)
        if key not in self._trends:
            self._trends[key] = ConsumerTrend(consumer_id=consumer_id)
        self._trends[key].daily_counts.append(count)
        return self._trends[key]

    def get(self, installation_id: str, consumer_id: str) -> ConsumerTrend | None:
        return self._trends.get((installation_id, consumer_id))

    def growing(self, installation_id: str) -> list[ConsumerTrend]:
        return [t for (inst, _), t in self._trends.items() if inst == installation_id and t.trend == "growing"]

    def declining(self, installation_id: str) -> list[ConsumerTrend]:
        return [t for (inst, _), t in self._trends.items() if inst == installation_id and t.trend == "declining"]

    def top_consumers(self, installation_id: str, limit: int = 10) -> list[ConsumerTrend]:
        trends = [t for (inst, _), t in self._trends.items() if inst == installation_id]
        return sorted(trends, key=lambda t: t.total, reverse=True)[:limit]
