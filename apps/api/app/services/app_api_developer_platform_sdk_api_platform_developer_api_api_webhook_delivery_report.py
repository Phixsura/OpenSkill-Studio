"""API Webhook Delivery Report — generate delivery performance reports."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class DeliveryMetrics:
    total_deliveries: int = 0
    successful: int = 0
    failed: int = 0
    retried: int = 0
    avg_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    total_bytes: int = 0

@dataclass
class ConsumerDeliveryReport:
    consumer_id: str
    period: str
    metrics: DeliveryMetrics
    top_failing_events: list[str] = field(default_factory=list)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiWebhookDeliveryReport:
    def __init__(self) -> None:
        self._metrics: dict[tuple[str, str], DeliveryMetrics] = {}

    def record_delivery(self, installation_id: str, consumer_id: str, success: bool, latency_ms: float, retried: bool = False, payload_bytes: int = 0) -> None:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, consumer_id)
        m = self._metrics.get(key)
        if m is None: m = DeliveryMetrics(); self._metrics[key] = m
        m.total_deliveries += 1
        m.total_bytes += payload_bytes
        if success: m.successful += 1
        else: m.failed += 1
        if retried: m.retried += 1
        # Running average
        m.avg_latency_ms = round(((m.avg_latency_ms * (m.total_deliveries - 1)) + latency_ms) / m.total_deliveries, 2)
        m.p99_latency_ms = max(m.p99_latency_ms, latency_ms)

    def generate_report(self, installation_id: str, consumer_id: str, period: str) -> ConsumerDeliveryReport:
        m = self._metrics.get((installation_id, consumer_id), DeliveryMetrics())
        return ConsumerDeliveryReport(consumer_id=consumer_id, period=period, metrics=m)

    def success_rate(self, installation_id: str, consumer_id: str) -> float:
        m = self._metrics.get((installation_id, consumer_id))
        if m is None or m.total_deliveries == 0: return 0.0
        return round((m.successful / m.total_deliveries) * 100, 1)

    def list_consumers(self, installation_id: str) -> list[str]:
        return list({cid for (inst, cid) in self._metrics if inst == installation_id})

    def overall_metrics(self, installation_id: str) -> DeliveryMetrics:
        overall = DeliveryMetrics()
        for (inst, _), m in self._metrics.items():
            if inst != installation_id: continue
            overall.total_deliveries += m.total_deliveries
            overall.successful += m.successful
            overall.failed += m.failed
            overall.retried += m.retried
            overall.total_bytes += m.total_bytes
            overall.p99_latency_ms = max(overall.p99_latency_ms, m.p99_latency_ms)
        if overall.total_deliveries > 0:
            overall.avg_latency_ms = round(sum(m.avg_latency_ms for (inst, _), m in self._metrics.items() if inst == installation_id) / len(self.list_consumers(installation_id)), 2)
        return overall
