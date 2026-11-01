"""App API Developer Webhook Delivery Metrics Aggregator — aggregate delivery metrics."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class DeliveryMetrics:
    period: str
    total_deliveries: int = 0
    successful: int = 0
    failed: int = 0
    retried: int = 0
    avg_latency_ms: float = 0.0
    total_bytes: int = 0

    @property
    def success_rate(self) -> float:
        return round(self.successful / self.total_deliveries * 100, 1) if self.total_deliveries > 0 else 100.0

    @property
    def retry_rate(self) -> float:
        return round(self.retried / self.total_deliveries * 100, 1) if self.total_deliveries > 0 else 0.0

class AppAPIDeveloperAPIApiDeveloperApiApiWebhookDeliveryMetricsAggregator:
    def __init__(self) -> None:
        self._metrics: dict[tuple[str, str], DeliveryMetrics] = {}

    def record(self, installation_id: str, period: str, total: int, successful: int, failed: int, retried: int, avg_latency_ms: float, total_bytes: int) -> DeliveryMetrics:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, period)
        m = DeliveryMetrics(period=period, total_deliveries=total, successful=successful, failed=failed, retried=retried, avg_latency_ms=avg_latency_ms, total_bytes=total_bytes)
        self._metrics[key] = m
        return m

    def get(self, installation_id: str, period: str) -> DeliveryMetrics | None:
        return self._metrics.get((installation_id, period))

    def trend(self, installation_id: str) -> list[DeliveryMetrics]:
        metrics = [m for (inst, _), m in self._metrics.items() if inst == installation_id]
        return sorted(metrics, key=lambda m: m.period)

    def worst_period(self, installation_id: str) -> DeliveryMetrics | None:
        metrics = self.trend(installation_id)
        return min(metrics, key=lambda m: m.success_rate) if metrics else None
