"""API Consumer Quota Allocation — allocate and track per-consumer resource quotas."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class QuotaAllocation:
    consumer_id: str
    resource: str  # "requests", "storage_mb", "webhooks", "connections"
    limit: int
    used: int = 0

    @property
    def remaining(self) -> int:
        return max(0, self.limit - self.used)

    @property
    def usage_pct(self) -> float:
        return round((self.used / self.limit) * 100, 1) if self.limit > 0 else 0.0

    @property
    def exhausted(self) -> bool:
        return self.used >= self.limit

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerQuotaAllocation:
    VALID_RESOURCES = {"requests", "storage_mb", "webhooks", "connections"}

    def __init__(self) -> None:
        self._quotas: dict[tuple[str, str, str], QuotaAllocation] = {}

    def allocate(self, installation_id: str, consumer_id: str, resource: str, limit: int) -> QuotaAllocation:
        if not installation_id: raise ValueError("installation_id is required")
        if resource not in self.VALID_RESOURCES: raise ValueError(f"Invalid resource: {resource}")
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 0: raise ValueError("limit must be non-negative integer")
        key = (installation_id, consumer_id, resource)
        if key in self._quotas: raise ValueError(f"Quota for {consumer_id}/{resource} already exists")
        q = QuotaAllocation(consumer_id=consumer_id, resource=resource, limit=limit)
        self._quotas[key] = q
        return q

    def consume(self, installation_id: str, consumer_id: str, resource: str, amount: int = 1) -> QuotaAllocation:
        key = (installation_id, consumer_id, resource)
        q = self._quotas.get(key)
        if q is None: raise KeyError(f"No quota for {consumer_id}/{resource}")
        if not isinstance(amount, int) or isinstance(amount, bool) or amount < 1: raise ValueError("amount must be positive integer")
        if q.used + amount > q.limit: raise ValueError("Quota exceeded")
        q.used += amount
        return q

    def get_quota(self, installation_id: str, consumer_id: str, resource: str) -> QuotaAllocation:
        key = (installation_id, consumer_id, resource)
        q = self._quotas.get(key)
        if q is None: raise KeyError(f"No quota for {consumer_id}/{resource}")
        return q

    def list_quotas(self, installation_id: str, consumer_id: str | None = None) -> list[QuotaAllocation]:
        return [q for (inst, cid, _), q in self._quotas.items()
                if inst == installation_id and (consumer_id is None or cid == consumer_id)]

    def reset(self, installation_id: str, consumer_id: str, resource: str) -> QuotaAllocation:
        key = (installation_id, consumer_id, resource)
        q = self._quotas.get(key)
        if q is None: raise KeyError(f"No quota for {consumer_id}/{resource}")
        q.used = 0
        return q

    def near_limit(self, installation_id: str, threshold_pct: float = 80.0) -> list[QuotaAllocation]:
        return [q for (inst, _, _), q in self._quotas.items()
                if inst == installation_id and q.usage_pct >= threshold_pct]
