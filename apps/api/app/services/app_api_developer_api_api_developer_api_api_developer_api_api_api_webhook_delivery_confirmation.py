"""App API Developer Webhook Delivery Confirmation — track delivery confirmations."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class DeliveryConfirmation:
    delivery_id: str
    destination: str
    confirmed: bool = False
    confirmed_at: float | None = None
    confirmation_latency_ms: float = 0.0
    retry_count: int = 0

class AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiWebhookDeliveryConfirmation:
    def __init__(self) -> None:
        self._confirmations: dict[tuple[str, str], DeliveryConfirmation] = {}

    def create(self, installation_id: str, delivery_id: str, destination: str) -> DeliveryConfirmation:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, delivery_id)
        c = DeliveryConfirmation(delivery_id=delivery_id, destination=destination)
        self._confirmations[key] = c
        return c

    def confirm(self, installation_id: str, delivery_id: str, latency_ms: float) -> DeliveryConfirmation:
        key = (installation_id, delivery_id)
        c = self._confirmations.get(key)
        if c is None: raise KeyError(f"Delivery {delivery_id} not found")
        c.confirmed = True
        c.confirmed_at = time.time()
        c.confirmation_latency_ms = latency_ms
        return c

    def retry(self, installation_id: str, delivery_id: str) -> DeliveryConfirmation:
        key = (installation_id, delivery_id)
        c = self._confirmations.get(key)
        if c is None: raise KeyError(f"Delivery {delivery_id} not found")
        c.retry_count += 1
        return c

    def unconfirmed(self, installation_id: str) -> list[DeliveryConfirmation]:
        return [c for (inst, _), c in self._confirmations.items() if inst == installation_id and not c.confirmed]

    def confirmation_rate(self, installation_id: str) -> float:
        all_c = [c for (inst, _), c in self._confirmations.items() if inst == installation_id]
        if not all_c: return 100.0
        return round(sum(1 for c in all_c if c.confirmed) / len(all_c) * 100, 1)

    def avg_latency(self, installation_id: str) -> float:
        confirmed = [c for (inst, _), c in self._confirmations.items() if inst == installation_id and c.confirmed]
        if not confirmed: return 0.0
        return round(sum(c.confirmation_latency_ms for c in confirmed) / len(confirmed), 1)
