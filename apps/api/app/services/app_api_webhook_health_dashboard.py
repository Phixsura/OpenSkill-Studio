"""App API Webhook Health Dashboard — unified webhook health overview."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class WebhookHealthDashboard:
    total_destinations: int = 0
    healthy_count: int = 0
    degraded_count: int = 0
    down_count: int = 0
    success_rate: float = 100.0
    avg_latency_ms: float = 0.0
    circuit_breakers_open: int = 0
    dead_letter_count: int = 0

    @property
    def overall_status(self) -> str:
        if self.down_count > 0 or self.circuit_breakers_open > 0: return "critical"
        if self.degraded_count > 0 or self.success_rate < 95: return "degraded"
        return "healthy"

class AppAPIWebhookHealthDashboard:
    def __init__(self) -> None:
        self._dashboards: dict[str, WebhookHealthDashboard] = {}

    def update(self, installation_id: str, **kwargs) -> WebhookHealthDashboard:
        if not installation_id: raise ValueError("installation_id is required")
        if installation_id not in self._dashboards:
            self._dashboards[installation_id] = WebhookHealthDashboard()
        d = self._dashboards[installation_id]
        for k, v in kwargs.items():
            if hasattr(d, k): setattr(d, k, v)
        return d

    def get(self, installation_id: str) -> WebhookHealthDashboard:
        return self._dashboards.get(installation_id, WebhookHealthDashboard())
