"""App Quota Allocation — allocate and track resource quotas.

Manages resource quotas for installed apps:
- Define quotas per resource type (API calls, storage, bandwidth)
- Track current usage against limits
- Percentage-based threshold alerts
- Per-installation scoped quotas
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class Quota:
    """A resource quota."""

    resource: str
    limit: int
    used: int = 0
    unit: str = "units"

    @property
    def remaining(self) -> int:
        return max(0, self.limit - self.used)

    @property
    def usage_pct(self) -> float:
        if self.limit == 0:
            return 100.0
        return round(self.used / self.limit * 100, 1)

    @property
    def exceeded(self) -> bool:
        return self.used >= self.limit


class AppQuotaAllocation:
    """Allocate and track resource quotas."""

    def __init__(self) -> None:
        self._quotas: dict[tuple[str, str], Quota] = {}

    def set_quota(
        self, installation_id: str, resource: str, limit: int, unit: str = "units",
    ) -> Quota:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not resource:
            raise ValueError("resource is required")
        if limit < 0:
            raise ValueError("limit must be non-negative")

        q = Quota(resource=resource, limit=limit, unit=unit)
        self._quotas[(installation_id, resource)] = q
        return q

    def consume(self, installation_id: str, resource: str, amount: int = 1) -> Quota:
        q = self._get(installation_id, resource)
        if amount < 0:
            raise ValueError("amount must be non-negative")
        if q.used + amount > q.limit:
            raise ValueError(f"Quota exceeded: {q.used + amount}/{q.limit} {q.unit}")
        q.used += amount
        return q

    def release(self, installation_id: str, resource: str, amount: int = 1) -> Quota:
        q = self._get(installation_id, resource)
        if amount < 0:
            raise ValueError("amount must be non-negative")
        q.used = max(0, q.used - amount)
        return q

    def check(self, installation_id: str, resource: str) -> Quota:
        return self._get(installation_id, resource)

    def alerts(self, installation_id: str, threshold_pct: float = 80.0) -> list[Quota]:
        """Return quotas that exceed the threshold percentage."""
        return [
            q for (inst, _), q in self._quotas.items()
            if inst == installation_id and q.usage_pct >= threshold_pct
        ]

    def list_quotas(self, installation_id: str) -> list[Quota]:
        return [q for (inst, _), q in self._quotas.items() if inst == installation_id]

    def reset(self, installation_id: str, resource: str) -> Quota:
        q = self._get(installation_id, resource)
        q.used = 0
        return q

    def _get(self, installation_id: str, resource: str) -> Quota:
        key = (installation_id, resource)
        q = self._quotas.get(key)
        if q is None:
            raise KeyError(f"Quota for '{resource}' not found")
        return q
