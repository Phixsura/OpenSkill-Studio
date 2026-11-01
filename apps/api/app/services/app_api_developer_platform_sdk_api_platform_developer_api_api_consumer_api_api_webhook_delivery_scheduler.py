"""API Consumer Webhook Delivery Scheduler — schedule delayed webhook deliveries."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class ScheduledDelivery:
    delivery_id: str
    event_id: str
    consumer_id: str
    deliver_at: float
    delivered: bool = False
    created_at: float = field(default_factory=time.time)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookDeliveryScheduler:
    def __init__(self) -> None:
        self._scheduled: dict[tuple[str, str], ScheduledDelivery] = {}

    def schedule(self, installation_id: str, delivery: ScheduledDelivery) -> ScheduledDelivery:
        if not installation_id: raise ValueError("installation_id is required")
        if delivery.deliver_at < delivery.created_at: raise ValueError("deliver_at must be in the future")
        key = (installation_id, delivery.delivery_id)
        if key in self._scheduled: raise ValueError(f"Delivery {delivery.delivery_id} already scheduled")
        self._scheduled[key] = delivery
        return delivery

    def due_deliveries(self, installation_id: str) -> list[ScheduledDelivery]:
        now = time.time()
        return [d for (inst, _), d in self._scheduled.items()
                if inst == installation_id and not d.delivered and d.deliver_at <= now]

    def mark_delivered(self, installation_id: str, delivery_id: str) -> ScheduledDelivery:
        key = (installation_id, delivery_id)
        d = self._scheduled.get(key)
        if d is None: raise KeyError(f"Delivery {delivery_id} not found")
        d.delivered = True
        return d

    def pending_count(self, installation_id: str) -> int:
        return sum(1 for (inst, _), d in self._scheduled.items() if inst == installation_id and not d.delivered)

    def cancel(self, installation_id: str, delivery_id: str) -> bool:
        key = (installation_id, delivery_id)
        d = self._scheduled.get(key)
        if d and not d.delivered: del self._scheduled[key]; return True
        return False

    def list_scheduled(self, installation_id: str) -> list[ScheduledDelivery]:
        return [d for (inst, _), d in self._scheduled.items() if inst == installation_id]
