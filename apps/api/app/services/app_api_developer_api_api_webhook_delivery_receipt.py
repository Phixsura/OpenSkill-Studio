"""App API Developer Webhook Delivery Receipt — confirm delivery acknowledgment."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class DeliveryReceipt:
    delivery_id: str
    destination: str
    status_code: int
    acknowledged: bool = False
    acknowledged_at: float | None = None
    response_time_ms: float = 0.0
    retry_number: int = 0

class AppAPIDeveloperAPIApiWebhookDeliveryReceipt:
    def __init__(self) -> None:
        self._receipts: dict[tuple[str, str], DeliveryReceipt] = {}

    def create(self, installation_id: str, delivery_id: str, destination: str, status_code: int, response_time_ms: float, retry_number: int = 0) -> DeliveryReceipt:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, delivery_id)
        r = DeliveryReceipt(delivery_id=delivery_id, destination=destination, status_code=status_code, response_time_ms=response_time_ms, retry_number=retry_number, acknowledged=200 <= status_code < 300)
        if r.acknowledged: r.acknowledged_at = time.time()
        self._receipts[key] = r
        return r

    def get(self, installation_id: str, delivery_id: str) -> DeliveryReceipt:
        key = (installation_id, delivery_id)
        r = self._receipts.get(key)
        if r is None: raise KeyError(f"Receipt {delivery_id} not found")
        return r

    def unacknowledged(self, installation_id: str) -> list[DeliveryReceipt]:
        return [r for (inst, _), r in self._receipts.items() if inst == installation_id and not r.acknowledged]

    def ack_rate(self, installation_id: str) -> float:
        all_r = [r for (inst, _), r in self._receipts.items() if inst == installation_id]
        if not all_r: return 100.0
        return round(sum(1 for r in all_r if r.acknowledged) / len(all_r) * 100, 1)

    def avg_response_time(self, installation_id: str) -> float:
        all_r = [r for (inst, _), r in self._receipts.items() if inst == installation_id]
        if not all_r: return 0.0
        return round(sum(r.response_time_ms for r in all_r) / len(all_r), 1)
