"""App API Developer Webhook Delivery SLA — SLA tracking for webhook deliveries."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class DeliverySLA:
    destination: str
    target_delivery_ms: int
    target_success_rate_pct: float
    actual_avg_ms: float = 0.0
    actual_success_rate_pct: float = 100.0
    total_deliveries: int = 0
    sla_breaches: int = 0

    @property
    def meeting_latency_sla(self) -> bool:
        return self.actual_avg_ms <= self.target_delivery_ms

    @property
    def meeting_success_sla(self) -> bool:
        return self.actual_success_rate_pct >= self.target_success_rate_pct

    @property
    def meeting_all_sla(self) -> bool:
        return self.meeting_latency_sla and self.meeting_success_sla

class AppAPIDeveloperPlatformSDKWebhookDeliverySLA:
    def __init__(self) -> None:
        self._slas: dict[tuple[str, str], DeliverySLA] = {}

    def set_sla(self, installation_id: str, destination: str, target_delivery_ms: int, target_success_rate_pct: float) -> DeliverySLA:
        if not installation_id: raise ValueError("installation_id is required")
        if target_delivery_ms < 1: raise ValueError("target must be positive")
        if not 0 < target_success_rate_pct <= 100: raise ValueError("rate must be 0-100")
        key = (installation_id, destination)
        s = DeliverySLA(destination=destination, target_delivery_ms=target_delivery_ms, target_success_rate_pct=target_success_rate_pct)
        self._slas[key] = s
        return s

    def update(self, installation_id: str, destination: str, avg_ms: float, success_rate_pct: float, deliveries: int) -> DeliverySLA:
        key = (installation_id, destination)
        s = self._slas.get(key)
        if s is None: raise KeyError(f"No SLA for {destination}")
        s.actual_avg_ms = avg_ms
        s.actual_success_rate_pct = success_rate_pct
        s.total_deliveries += deliveries
        if not s.meeting_all_sla: s.sla_breaches += 1
        return s

    def breaching(self, installation_id: str) -> list[DeliverySLA]:
        return [s for (inst, _), s in self._slas.items() if inst == installation_id and not s.meeting_all_sla]

    def all_slas(self, installation_id: str) -> list[DeliverySLA]:
        return [s for (inst, _), s in self._slas.items() if inst == installation_id]
