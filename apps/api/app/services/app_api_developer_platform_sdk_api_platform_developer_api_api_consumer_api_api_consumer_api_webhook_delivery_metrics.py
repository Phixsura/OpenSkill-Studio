"""API Consumer Webhook Delivery Metrics — comprehensive delivery performance metrics."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class DeliveryMetrics:
    consumer_id: str
    total_deliveries: int = 0
    successful: int = 0
    failed: int = 0
    retried: int = 0
    total_latency_ms: float = 0.0
    max_latency_ms: float = 0.0

    @property
    def success_rate(self) -> float:
        if self.total_deliveries == 0: return 0.0
        return round((self.successful / self.total_deliveries) * 100, 1)

    @property
    def avg_latency_ms(self) -> float:
        if self.total_deliveries == 0: return 0.0
        return round(self.total_latency_ms / self.total_deliveries, 2)

    @property
    def retry_rate(self) -> float:
        if self.total_deliveries == 0: return 0.0
        return round((self.retried / self.total_deliveries) * 100, 1)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookDeliveryMetrics:
    def __init__(self) -> None:
        self._metrics: dict[tuple[str, str], DeliveryMetrics] = {}

    def record(self, installation_id: str, consumer_id: str, success: bool, latency_ms: float, retried: bool = False) -> DeliveryMetrics:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, consumer_id)
        m = self._metrics.get(key)
        if m is None:
            m = DeliveryMetrics(consumer_id=consumer_id)
            self._metrics[key] = m
        m.total_deliveries += 1
        m.total_latency_ms += latency_ms
        m.max_latency_ms = max(m.max_latency_ms, latency_ms)
        if success: m.successful += 1
        else: m.failed += 1
        if retried: m.retried += 1
        return m

    def get_metrics(self, installation_id: str, consumer_id: str) -> DeliveryMetrics | None:
        return self._metrics.get((installation_id, consumer_id))

    def worst_performers(self, installation_id: str, limit: int = 5) -> list[DeliveryMetrics]:
        metrics = [m for (inst, _), m in self._metrics.items() if inst == installation_id and m.total_deliveries > 0]
        return sorted(metrics, key=lambda m: m.success_rate)[:limit]

    def list_metrics(self, installation_id: str) -> list[DeliveryMetrics]:
        return [m for (inst, _), m in self._metrics.items() if inst == installation_id]
