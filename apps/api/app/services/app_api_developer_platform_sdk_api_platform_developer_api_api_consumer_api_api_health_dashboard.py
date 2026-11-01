"""API Consumer Health Dashboard — aggregate health metrics across all consumers."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class DashboardMetrics:
    total_consumers: int = 0
    active_consumers: int = 0
    total_requests_today: int = 0
    error_rate_pct: float = 0.0
    avg_latency_ms: float = 0.0
    uptime_pct: float = 100.0
    active_incidents: int = 0
    open_tickets: int = 0

@dataclass
class ConsumerSummary:
    consumer_id: str
    health_score: int
    requests_today: int
    error_rate: float
    status: str  # "healthy", "degraded", "critical"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiHealthDashboard:
    def __init__(self) -> None:
        self._metrics: dict[str, DashboardMetrics] = {}
        self._summaries: dict[tuple[str, str], ConsumerSummary] = {}

    def update_metrics(self, installation_id: str, metrics: DashboardMetrics) -> DashboardMetrics:
        if not installation_id: raise ValueError("installation_id is required")
        self._metrics[installation_id] = metrics
        return metrics

    def update_consumer(self, installation_id: str, summary: ConsumerSummary) -> ConsumerSummary:
        if not installation_id: raise ValueError("installation_id is required")
        self._summaries[(installation_id, summary.consumer_id)] = summary
        return summary

    def get_dashboard(self, installation_id: str) -> DashboardMetrics:
        return self._metrics.get(installation_id, DashboardMetrics())

    def top_consumers(self, installation_id: str, limit: int = 10) -> list[ConsumerSummary]:
        summaries = [s for (inst, _), s in self._summaries.items() if inst == installation_id]
        return sorted(summaries, key=lambda s: -s.requests_today)[:limit]

    def degraded_consumers(self, installation_id: str) -> list[ConsumerSummary]:
        return [s for (inst, _), s in self._summaries.items() if inst == installation_id and s.status in ("degraded", "critical")]

    def overall_health(self, installation_id: str) -> str:
        m = self.get_dashboard(installation_id)
        if m.active_incidents > 0 or m.error_rate_pct > 10: return "critical"
        if m.error_rate_pct > 5 or m.uptime_pct < 99.5: return "degraded"
        return "healthy"
