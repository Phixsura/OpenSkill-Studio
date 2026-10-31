"""Platform Summary Dashboard — comprehensive platform-wide summary."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class PlatformMetric:
    name: str
    value: float
    unit: str = ""
    trend: str = "stable"

@dataclass
class PlatformSummary:
    total_consumers: int = 0
    active_consumers: int = 0
    total_api_keys: int = 0
    total_webhooks: int = 0
    total_requests_today: int = 0
    avg_latency_ms: float = 0.0
    error_rate_pct: float = 0.0
    uptime_pct: float = 100.0
    health_score: float = 100.0
    metrics: list[PlatformMetric] = field(default_factory=list)
    active_incidents: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiPlatformSummaryDashboard:
    def __init__(self) -> None:
        self._summaries: dict[str, PlatformSummary] = {}

    def update(self, installation_id: str, summary: PlatformSummary) -> PlatformSummary:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not (0 <= summary.health_score <= 100):
            raise ValueError("health_score must be 0-100")
        if not (0 <= summary.uptime_pct <= 100):
            raise ValueError("uptime_pct must be 0-100")
        self._summaries[installation_id] = summary
        log.info("platform_summary_updated", installation_id=installation_id, consumers=summary.total_consumers, health=summary.health_score)
        return summary

    def get(self, installation_id: str) -> PlatformSummary:
        return self._summaries.get(installation_id, PlatformSummary())

    def compute_health(self, error_rate: float, avg_latency_ms: float, uptime_pct: float) -> float:
        err_score = max(0, min(100, 100 - error_rate * 10))
        lat_score = max(0, min(100, 100 - (avg_latency_ms / 20)))
        up_score = max(0, min(100, (uptime_pct - 95) * 20))
        return round(err_score * 0.4 + lat_score * 0.3 + up_score * 0.3, 1)
