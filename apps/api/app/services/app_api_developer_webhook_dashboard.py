"""App API Developer Webhook Dashboard — unified webhook management view."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class WebhookDashboardSummary:
    total_destinations: int = 0
    active_subscriptions: int = 0
    total_delivered: int = 0
    total_failed: int = 0
    dead_letter_count: int = 0
    circuit_breakers_open: int = 0
    avg_delivery_ms: float = 0.0
    success_rate: float = 100.0

class AppAPIDeveloperWebhookDashboard:
    def __init__(self) -> None:
        self._dashboards: dict[str, WebhookDashboardSummary] = {}

    def update(self, installation_id: str, **kwargs) -> WebhookDashboardSummary:
        if not installation_id: raise ValueError("installation_id is required")
        if installation_id not in self._dashboards:
            self._dashboards[installation_id] = WebhookDashboardSummary()
        d = self._dashboards[installation_id]
        for k, v in kwargs.items():
            if hasattr(d, k): setattr(d, k, v)
        return d

    def get(self, installation_id: str) -> WebhookDashboardSummary:
        return self._dashboards.get(installation_id, WebhookDashboardSummary())
