"""App API Developer API Quota Allocation — allocate and track API quotas per consumer."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class QuotaAllocation:
    consumer_id: str
    quota_type: str  # "daily", "monthly"
    allocated: int
    used: int = 0

    @property
    def remaining(self) -> int:
        return max(0, self.allocated - self.used)

    @property
    def usage_pct(self) -> float:
        return round(self.used / self.allocated * 100, 1) if self.allocated > 0 else 0.0

    @property
    def exhausted(self) -> bool:
        return self.used >= self.allocated

class AppAPIDeveloperAPIApiQuotaAllocation:
    def __init__(self) -> None:
        self._quotas: dict[tuple[str, str, str], QuotaAllocation] = {}

    def allocate(self, installation_id: str, consumer_id: str, quota_type: str, amount: int) -> QuotaAllocation:
        if not installation_id: raise ValueError("installation_id is required")
        if quota_type not in ("daily", "monthly"): raise ValueError("invalid quota_type")
        if amount <= 0: raise ValueError("amount must be positive")
        key = (installation_id, consumer_id, quota_type)
        q = QuotaAllocation(consumer_id=consumer_id, quota_type=quota_type, allocated=amount)
        self._quotas[key] = q
        return q

    def consume(self, installation_id: str, consumer_id: str, quota_type: str, amount: int = 1) -> QuotaAllocation:
        key = (installation_id, consumer_id, quota_type)
        q = self._quotas.get(key)
        if q is None: raise KeyError(f"No quota for {consumer_id}/{quota_type}")
        if q.exhausted: raise ValueError("Quota exhausted")
        q.used += amount
        return q

    def check(self, installation_id: str, consumer_id: str, quota_type: str) -> QuotaAllocation | None:
        return self._quotas.get((installation_id, consumer_id, quota_type))

    def exhausted_consumers(self, installation_id: str) -> list[QuotaAllocation]:
        return [q for (inst, _, _), q in self._quotas.items() if inst == installation_id and q.exhausted]

    def reset(self, installation_id: str, consumer_id: str, quota_type: str) -> QuotaAllocation:
        key = (installation_id, consumer_id, quota_type)
        q = self._quotas.get(key)
        if q is None: raise KeyError(f"No quota")
        q.used = 0
        return q
