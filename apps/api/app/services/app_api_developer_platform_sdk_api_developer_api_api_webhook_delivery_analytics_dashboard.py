"""App API Developer Webhook Delivery Analytics Dashboard — comprehensive delivery overview."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class DeliveryAnalyticsDashboard:
    total_deliveries: int = 0
    successful: int = 0
    failed: int = 0
    retried: int = 0
    avg_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    active_destinations: int = 0
    dead_letters: int = 0
    queue_depth: int = 0

    @property
    def success_rate(self) -> float:
        return round(self.successful / self.total_deliveries * 100, 1) if self.total_deliveries > 0 else 100.0

    @property
    def retry_rate(self) -> float:
        return round(self.retried / self.total_deliveries * 100, 1) if self.total_deliveries > 0 else 0.0

    @property
    def health(self) -> str:
        if self.success_rate >= 99 and self.p99_latency_ms < 1000 and self.dead_letters == 0: return "excellent"
        if self.success_rate >= 95: return "good"
        if self.success_rate >= 90: return "fair"
        return "poor"

class AppAPIDeveloperPlatformSDKApiDeveloperApiApiWebhookDeliveryAnalyticsDashboard:
    def __init__(self) -> None:
        self._dashboards: dict[str, DeliveryAnalyticsDashboard] = {}

    def update(self, installation_id: str, **kwargs) -> DeliveryAnalyticsDashboard:
        if not installation_id: raise ValueError("installation_id is required")
        d = DeliveryAnalyticsDashboard()
        for k, v in kwargs.items():
            if hasattr(d, k): setattr(d, k, v)
        self._dashboards[installation_id] = d
        return d

    def get(self, installation_id: str) -> DeliveryAnalyticsDashboard:
        return self._dashboards.get(installation_id, DeliveryAnalyticsDashboard())
