"""Extension Usage Metering — track billable usage per extension/user."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class UsageMeter:
    meter_id: str
    extension_id: str
    user_id: str
    metric: str  # api_calls, compute_minutes, storage_mb, bandwidth_gb
    quantity: float = 0.0
    unit_price_cents: int = 0  # price per unit in cents
    period_start: float = 0.0
    def __post_init__(self):
        if not self.period_start: self.period_start = time.time()

    @property
    def total_cents(self) -> int:
        return round(self.quantity * self.unit_price_cents)


class ExtUsageMeteringService:
    def __init__(self):
        self._meters: dict[str, UsageMeter] = {}  # key: ext:user:metric

    def _key(self, ext_id: str, user_id: str, metric: str) -> str:
        return f"{ext_id}:{user_id}:{metric}"

    def configure(self, extension_id: str, user_id: str, metric: str,
                  unit_price_cents: int) -> UsageMeter:
        key = self._key(extension_id, user_id, metric)
        meter = UsageMeter(meter_id=key, extension_id=extension_id,
                           user_id=user_id, metric=metric,
                           unit_price_cents=unit_price_cents)
        self._meters[key] = meter
        return meter

    def record(self, extension_id: str, user_id: str, metric: str,
               quantity: float = 1.0) -> float:
        key = self._key(extension_id, user_id, metric)
        meter = self._meters.get(key)
        if not meter:
            meter = self.configure(extension_id, user_id, metric, 0)
        meter.quantity += quantity
        return meter.quantity

    def get_bill(self, extension_id: str, user_id: str) -> dict:
        items = []
        total = 0
        for m in self._meters.values():
            if m.extension_id == extension_id and m.user_id == user_id and m.quantity > 0:
                items.append({"metric": m.metric, "quantity": m.quantity,
                              "unit_price": m.unit_price_cents, "total": m.total_cents})
                total += m.total_cents
        return {"items": items, "total_cents": total}

    def reset_period(self, extension_id: str, user_id: str) -> None:
        for m in self._meters.values():
            if m.extension_id == extension_id and m.user_id == user_id:
                m.quantity = 0
                m.period_start = time.time()
