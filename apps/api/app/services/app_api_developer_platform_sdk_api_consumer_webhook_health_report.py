"""App API Developer Consumer Webhook Health Report — per-consumer webhook health."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ConsumerWebhookHealth:
    consumer_id: str
    destinations: int = 0
    active_destinations: int = 0
    total_deliveries: int = 0
    successful_deliveries: int = 0
    failed_deliveries: int = 0
    avg_latency_ms: float = 0.0

    @property
    def success_rate(self) -> float:
        return round(self.successful_deliveries / self.total_deliveries * 100, 1) if self.total_deliveries > 0 else 100.0

    @property
    def health_grade(self) -> str:
        r = self.success_rate
        if r >= 99: return "A"
        if r >= 95: return "B"
        if r >= 90: return "C"
        return "D"

class AppAPIDeveloperPlatformSDKApiConsumerWebhookHealthReport:
    def __init__(self) -> None:
        self._reports: dict[tuple[str, str], ConsumerWebhookHealth] = {}

    def update(self, installation_id: str, consumer_id: str, **kwargs) -> ConsumerWebhookHealth:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, consumer_id)
        h = ConsumerWebhookHealth(consumer_id=consumer_id)
        for k, v in kwargs.items():
            if hasattr(h, k): setattr(h, k, v)
        self._reports[key] = h
        return h

    def get(self, installation_id: str, consumer_id: str) -> ConsumerWebhookHealth:
        return self._reports.get((installation_id, consumer_id), ConsumerWebhookHealth(consumer_id=consumer_id))

    def unhealthy(self, installation_id: str) -> list[ConsumerWebhookHealth]:
        return [h for (inst, _), h in self._reports.items() if inst == installation_id and h.health_grade in ("C", "D")]

    def ranked(self, installation_id: str) -> list[ConsumerWebhookHealth]:
        reports = [h for (inst, _), h in self._reports.items() if inst == installation_id]
        return sorted(reports, key=lambda h: h.success_rate)
