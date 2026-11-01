"""App API Webhook Analytics — comprehensive webhook analytics dashboard."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class WebhookAnalytics:
    total_sent: int = 0
    total_failed: int = 0
    avg_latency_ms: float = 0.0
    active_destinations: int = 0
    top_event_type: str = ""
    top_event_count: int = 0

    @property
    def success_rate(self) -> float:
        total = self.total_sent + self.total_failed
        if total == 0: return 100.0
        return round(self.total_sent / total * 100, 1)

class AppAPIWebhookAnalytics:
    def __init__(self) -> None:
        self._analytics: dict[str, WebhookAnalytics] = {}

    def update(self, installation_id: str, **kwargs) -> WebhookAnalytics:
        if not installation_id: raise ValueError("installation_id is required")
        if installation_id not in self._analytics:
            self._analytics[installation_id] = WebhookAnalytics()
        a = self._analytics[installation_id]
        for k, v in kwargs.items():
            if hasattr(a, k): setattr(a, k, v)
        return a

    def get(self, installation_id: str) -> WebhookAnalytics:
        return self._analytics.get(installation_id, WebhookAnalytics())
