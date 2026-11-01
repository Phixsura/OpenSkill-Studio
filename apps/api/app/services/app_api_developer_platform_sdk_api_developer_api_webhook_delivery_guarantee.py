"""App API Developer Webhook Delivery Guarantee — track at-least-once delivery guarantees."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class DeliveryGuarantee:
    destination: str
    guarantee_type: str = "at_least_once"  # "at_least_once", "at_most_once", "exactly_once"
    total_attempts: int = 0
    successful_first_try: int = 0
    successful_after_retry: int = 0
    permanently_failed: int = 0

    @property
    def first_try_rate(self) -> float:
        return round(self.successful_first_try / self.total_attempts * 100, 1) if self.total_attempts > 0 else 100.0

    @property
    def overall_delivery_rate(self) -> float:
        delivered = self.successful_first_try + self.successful_after_retry
        return round(delivered / self.total_attempts * 100, 1) if self.total_attempts > 0 else 100.0

    @property
    def guarantee_met(self) -> bool:
        if self.guarantee_type == "at_least_once": return self.overall_delivery_rate >= 99.9
        if self.guarantee_type == "exactly_once": return self.overall_delivery_rate >= 99.99
        return True

class AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookDeliveryGuarantee:
    def __init__(self) -> None:
        self._guarantees: dict[tuple[str, str], DeliveryGuarantee] = {}

    def configure(self, installation_id: str, destination: str, guarantee_type: str = "at_least_once") -> DeliveryGuarantee:
        if not installation_id: raise ValueError("installation_id is required")
        if guarantee_type not in ("at_least_once", "at_most_once", "exactly_once"): raise ValueError("invalid guarantee type")
        key = (installation_id, destination)
        g = DeliveryGuarantee(destination=destination, guarantee_type=guarantee_type)
        self._guarantees[key] = g
        return g

    def record(self, installation_id: str, destination: str, first_try: bool, retried: bool = False, failed: bool = False) -> DeliveryGuarantee:
        key = (installation_id, destination)
        g = self._guarantees.get(key)
        if g is None: raise KeyError(f"No guarantee for {destination}")
        g.total_attempts += 1
        if first_try: g.successful_first_try += 1
        elif retried: g.successful_after_retry += 1
        elif failed: g.permanently_failed += 1
        return g

    def unmet_guarantees(self, installation_id: str) -> list[DeliveryGuarantee]:
        return [g for (inst, _), g in self._guarantees.items() if inst == installation_id and not g.guarantee_met]

    def all_guarantees(self, installation_id: str) -> list[DeliveryGuarantee]:
        return [g for (inst, _), g in self._guarantees.items() if inst == installation_id]
