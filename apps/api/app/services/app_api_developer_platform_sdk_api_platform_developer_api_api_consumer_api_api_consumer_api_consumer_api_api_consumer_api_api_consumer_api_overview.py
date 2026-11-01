"""Consumer API Overview — unified dashboard summarizing all consumer API metrics."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class OverviewMetric:
    name: str
    value: float
    unit: str = ""
    trend: str = "stable"  # "up", "down", "stable"
    change_pct: float = 0.0

@dataclass
class ConsumerOverview:
    consumer_id: str
    plan: str
    status: str  # "active", "suspended", "trial"
    metrics: list[OverviewMetric] = field(default_factory=list)
    active_keys: int = 0
    active_webhooks: int = 0
    team_members: int = 0
    health_score: float = 100.0
    onboarding_complete: bool = False

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiOverview:
    def __init__(self) -> None:
        self._overviews: dict[tuple[str, str], ConsumerOverview] = {}

    def update(self, installation_id: str, overview: ConsumerOverview) -> ConsumerOverview:
        if not installation_id:
            raise ValueError("installation_id is required")
        if overview.status not in ("active", "suspended", "trial"):
            raise ValueError(f"Invalid status: {overview.status}")
        if not (0 <= overview.health_score <= 100):
            raise ValueError("health_score must be 0-100")
        self._overviews[(installation_id, overview.consumer_id)] = overview
        return overview

    def get(self, installation_id: str, consumer_id: str) -> ConsumerOverview | None:
        return self._overviews.get((installation_id, consumer_id))

    def list_all(self, installation_id: str, status: str | None = None) -> list[ConsumerOverview]:
        overviews = [o for (inst, _), o in self._overviews.items() if inst == installation_id]
        if status:
            overviews = [o for o in overviews if o.status == status]
        return sorted(overviews, key=lambda o: -o.health_score)

    def get_platform_summary(self, installation_id: str) -> dict[str, int | float]:
        overviews = [o for (inst, _), o in self._overviews.items() if inst == installation_id]
        if not overviews:
            return {"total_consumers": 0, "active": 0, "avg_health": 0}
        active = sum(1 for o in overviews if o.status == "active")
        avg_health = sum(o.health_score for o in overviews) / len(overviews)
        return {"total_consumers": len(overviews), "active": active, "suspended": sum(1 for o in overviews if o.status == "suspended"), "avg_health": round(avg_health, 1), "total_keys": sum(o.active_keys for o in overviews), "total_webhooks": sum(o.active_webhooks for o in overviews)}
