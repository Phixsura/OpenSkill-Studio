"""App API Webhook Delivery Receipt — track delivery acknowledgments."""
from __future__ import annotations
import time
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class DeliveryReceipt:
    receipt_id: str
    delivery_id: str
    destination: str
    status_code: int
    response_time_ms: float
    acknowledged: bool = False
    received_at: float = field(default_factory=time.time)

class AppAPIWebhookDeliveryReceipt:
    def __init__(self) -> None:
        self._receipts: dict[str, list[DeliveryReceipt]] = {}

    def record(self, installation_id: str, receipt_id: str, delivery_id: str, destination: str, status_code: int, response_time_ms: float) -> DeliveryReceipt:
        if not installation_id: raise ValueError("installation_id is required")
        r = DeliveryReceipt(receipt_id=receipt_id, delivery_id=delivery_id, destination=destination, status_code=status_code, response_time_ms=response_time_ms, acknowledged=200 <= status_code < 300)
        self._receipts.setdefault(installation_id, []).append(r)
        return r

    def acknowledged_rate(self, installation_id: str) -> float:
        receipts = self._receipts.get(installation_id, [])
        if not receipts: return 100.0
        acked = sum(1 for r in receipts if r.acknowledged)
        return round(acked / len(receipts) * 100, 1)

    def recent(self, installation_id: str, limit: int = 20) -> list[DeliveryReceipt]:
        return list(reversed(self._receipts.get(installation_id, [])[-limit:]))

    def count(self, installation_id: str) -> int:
        return len(self._receipts.get(installation_id, []))
