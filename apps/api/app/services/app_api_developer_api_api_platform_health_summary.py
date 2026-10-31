"""App API Developer Platform Health Summary — the grand unified health dashboard."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class PlatformHealthSummary:
    # Core metrics
    api_uptime_pct: float = 100.0
    avg_latency_ms: float = 0.0
    error_rate_pct: float = 0.0
    # Webhooks
    webhook_success_rate_pct: float = 100.0
    webhook_queue_depth: int = 0
    # Consumers
    active_consumers: int = 0
    total_api_calls_24h: int = 0
    # Security
    security_score: int = 100
    open_findings: int = 0
    # Infrastructure
    services_healthy: int = 0
    services_total: int = 0
    circuits_open: int = 0

    @property
    def overall_health(self) -> str:
        if self.api_uptime_pct < 99 or self.error_rate_pct > 5 or self.circuits_open > 0: return "critical"
        if self.api_uptime_pct < 99.9 or self.error_rate_pct > 1 or self.webhook_success_rate_pct < 95: return "degraded"
        if self.open_findings > 0 or self.webhook_queue_depth > 1000: return "warning"
        return "healthy"

    @property
    def health_score(self) -> int:
        score = 100
        if self.api_uptime_pct < 99.9: score -= 20
        if self.error_rate_pct > 1: score -= 15
        if self.webhook_success_rate_pct < 99: score -= 10
        if self.open_findings > 0: score -= min(self.open_findings * 5, 20)
        if self.circuits_open > 0: score -= 15
        if self.avg_latency_ms > 500: score -= 10
        return max(0, score)

class AppAPIDeveloperAPIApiPlatformHealthSummary:
    def __init__(self) -> None:
        self._summaries: dict[str, PlatformHealthSummary] = {}

    def update(self, installation_id: str, **kwargs) -> PlatformHealthSummary:
        if not installation_id: raise ValueError("installation_id is required")
        s = PlatformHealthSummary()
        for k, v in kwargs.items():
            if hasattr(s, k): setattr(s, k, v)
        self._summaries[installation_id] = s
        return s

    def get(self, installation_id: str) -> PlatformHealthSummary:
        return self._summaries.get(installation_id, PlatformHealthSummary())
