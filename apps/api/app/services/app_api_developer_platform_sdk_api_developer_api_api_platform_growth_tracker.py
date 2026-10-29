"""App API Developer Platform Growth Tracker — track platform growth metrics over time."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class GrowthSnapshot:
    period: str
    total_consumers: int = 0
    new_consumers: int = 0
    churned_consumers: int = 0
    total_api_calls: int = 0
    mrr_cents: int = 0

    @property
    def net_growth(self) -> int:
        return self.new_consumers - self.churned_consumers

    @property
    def churn_rate_pct(self) -> float:
        return round(self.churned_consumers / self.total_consumers * 100, 1) if self.total_consumers > 0 else 0.0

    @property
    def growth_healthy(self) -> bool:
        return self.net_growth > 0 and self.churn_rate_pct < 5

class AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformGrowthTracker:
    def __init__(self) -> None:
        self._snapshots: dict[tuple[str, str], GrowthSnapshot] = {}

    def record(self, installation_id: str, period: str, **kwargs) -> GrowthSnapshot:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, period)
        s = GrowthSnapshot(period=period)
        for k, v in kwargs.items():
            if hasattr(s, k): setattr(s, k, v)
        self._snapshots[key] = s
        return s

    def trend(self, installation_id: str) -> list[GrowthSnapshot]:
        snaps = [s for (inst, _), s in self._snapshots.items() if inst == installation_id]
        return sorted(snaps, key=lambda s: s.period)

    def latest(self, installation_id: str) -> GrowthSnapshot | None:
        t = self.trend(installation_id)
        return t[-1] if t else None

    def total_mrr(self, installation_id: str) -> int:
        latest = self.latest(installation_id)
        return latest.mrr_cents if latest else 0
