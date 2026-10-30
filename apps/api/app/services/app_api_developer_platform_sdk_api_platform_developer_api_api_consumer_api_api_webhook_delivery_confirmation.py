"""API Consumer Webhook Delivery Confirmation — require consumer confirmation of receipt."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import time
import structlog

log = structlog.get_logger()

class ConfirmationStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    TIMEOUT = "timeout"

@dataclass
class DeliveryConfirmation:
    delivery_id: str
    event_id: str
    consumer_id: str
    status: ConfirmationStatus = ConfirmationStatus.PENDING
    delivered_at: float = field(default_factory=time.time)
    confirmed_at: float = 0.0
    timeout_s: int = 30

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookDeliveryConfirmation:
    def __init__(self) -> None:
        self._deliveries: dict[tuple[str, str], DeliveryConfirmation] = {}
        self._stats: dict[str, dict[str, int]] = {}

    def record_delivery(self, installation_id: str, delivery: DeliveryConfirmation) -> DeliveryConfirmation:
        if not installation_id: raise ValueError("installation_id is required")
        self._deliveries[(installation_id, delivery.delivery_id)] = delivery
        return delivery

    def confirm(self, installation_id: str, delivery_id: str) -> DeliveryConfirmation:
        key = (installation_id, delivery_id)
        d = self._deliveries.get(key)
        if d is None: raise KeyError(f"Delivery {delivery_id} not found")
        if d.status != ConfirmationStatus.PENDING: raise ValueError(f"Already {d.status.value}")
        d.status = ConfirmationStatus.CONFIRMED
        d.confirmed_at = time.time()
        self._stats.setdefault(installation_id, {"confirmed": 0, "timeout": 0})["confirmed"] += 1
        return d

    def check_timeouts(self, installation_id: str) -> list[DeliveryConfirmation]:
        now = time.time()
        timed_out = []
        for (inst, _), d in self._deliveries.items():
            if inst == installation_id and d.status == ConfirmationStatus.PENDING:
                if now - d.delivered_at > d.timeout_s:
                    d.status = ConfirmationStatus.TIMEOUT
                    self._stats.setdefault(installation_id, {"confirmed": 0, "timeout": 0})["timeout"] += 1
                    timed_out.append(d)
        return timed_out

    def confirmation_rate(self, installation_id: str) -> float:
        s = self._stats.get(installation_id, {"confirmed": 0, "timeout": 0})
        total = s["confirmed"] + s["timeout"]
        return round((s["confirmed"] / total) * 100, 1) if total > 0 else 0.0

    def pending_count(self, installation_id: str) -> int:
        return sum(1 for (inst, _), d in self._deliveries.items() if inst == installation_id and d.status == ConfirmationStatus.PENDING)
