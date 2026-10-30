"""API Consumer Usage Dashboard — unified per-consumer usage dashboard."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ConsumerDashboard:
    consumer_id: str
    requests_today: int = 0
    requests_this_month: int = 0
    success_rate: float = 100.0
    avg_latency_ms: float = 0.0
    active_api_keys: int = 0
    webhook_subscriptions: int = 0
    quota_usage_pct: float = 0.0
    health_score: int = 100
    tier: str = "free"

    @property
    def status(self) -> str:
        if self.health_score >= 80: return "healthy"
        if self.health_score >= 50: return "degraded"
        return "critical"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiUsageDashboard:
    def __init__(self) -> None:
        self._dashboards: dict[tuple[str, str], ConsumerDashboard] = {}

    def update(self, installation_id: str, dashboard: ConsumerDashboard) -> ConsumerDashboard:
        if not installation_id: raise ValueError("installation_id is required")
        self._dashboards[(installation_id, dashboard.consumer_id)] = dashboard
        return dashboard

    def get_dashboard(self, installation_id: str, consumer_id: str) -> ConsumerDashboard | None:
        return self._dashboards.get((installation_id, consumer_id))

    def top_consumers(self, installation_id: str, limit: int = 10) -> list[ConsumerDashboard]:
        dashes = [d for (inst, _), d in self._dashboards.items() if inst == installation_id]
        return sorted(dashes, key=lambda d: -d.requests_today)[:limit]

    def degraded_consumers(self, installation_id: str) -> list[ConsumerDashboard]:
        return [d for (inst, _), d in self._dashboards.items() if inst == installation_id and d.status != "healthy"]

    def list_dashboards(self, installation_id: str) -> list[ConsumerDashboard]:
        return [d for (inst, _), d in self._dashboards.items() if inst == installation_id]
