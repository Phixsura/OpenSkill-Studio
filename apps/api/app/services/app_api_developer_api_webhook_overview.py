"""App API Developer Webhook Overview — the definitive webhook platform summary."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class WebhookOverview:
    """The ultimate webhook platform overview — combines all webhook metrics."""
    total_events_emitted: int = 0
    total_deliveries: int = 0
    total_destinations: int = 0
    total_subscriptions: int = 0
    success_rate: float = 100.0
    avg_delivery_ms: float = 0.0
    circuit_breakers_open: int = 0
    dead_letters: int = 0
    retry_rate: float = 0.0
    compression_savings_bytes: int = 0
    idempotency_dedup_count: int = 0
    active_filters: int = 0

class AppAPIDeveloperAPIWebhookOverview:
    def __init__(self) -> None:
        self._overviews: dict[str, WebhookOverview] = {}

    def update(self, installation_id: str, **kwargs) -> WebhookOverview:
        if not installation_id: raise ValueError("installation_id is required")
        if installation_id not in self._overviews:
            self._overviews[installation_id] = WebhookOverview()
        o = self._overviews[installation_id]
        for k, v in kwargs.items():
            if hasattr(o, k): setattr(o, k, v)
        return o

    def get(self, installation_id: str) -> WebhookOverview:
        return self._overviews.get(installation_id, WebhookOverview())
