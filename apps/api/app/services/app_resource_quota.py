"""App Resource Quota — manage resource limits per installation.

Tracks resource usage against quotas:
- Define quotas per resource type
- Record consumption
- Check remaining capacity
- Alert when approaching limits
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class Quota:
    """A resource quota."""

    resource: str
    limit: float
    used: float = 0.0

    @property
    def remaining(self) -> float:
        return max(0.0, self.limit - self.used)

    @property
    def usage_pct(self) -> float:
        return round(self.used / self.limit * 100, 1) if self.limit > 0 else 0.0

    @property
    def exceeded(self) -> bool:
        return self.used >= self.limit


class AppResourceQuota:
    """Manage resource limits per installation."""

    def __init__(self) -> None:
        self._quotas: dict[tuple[str, str], Quota] = {}

    def set_quota(
        self, installation_id: str, resource: str, limit: float
    ) -> Quota:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not resource:
            raise ValueError("resource is required")
        if limit <= 0:
            raise ValueError("limit must be positive")

        key = (installation_id, resource)
        existing = self._quotas.get(key)
        used = existing.used if existing else 0.0
        quota = Quota(resource=resource, limit=limit, used=used)
        self._quotas[key] = quota
        return quota

    def consume(
        self, installation_id: str, resource: str, amount: float
    ) -> Quota:
        """Consume resources. Raises if would exceed quota."""
        if amount <= 0:
            raise ValueError("amount must be positive")
        quota = self._get(installation_id, resource)
        if quota.used + amount > quota.limit:
            raise ValueError(f"Would exceed quota: {quota.used + amount} > {quota.limit}")
        quota.used += amount
        return quota

    def release(
        self, installation_id: str, resource: str, amount: float
    ) -> Quota:
        """Release consumed resources."""
        if amount <= 0:
            raise ValueError("amount must be positive")
        quota = self._get(installation_id, resource)
        quota.used = max(0.0, quota.used - amount)
        return quota

    def can_consume(
        self, installation_id: str, resource: str, amount: float
    ) -> bool:
        quota = self._quotas.get((installation_id, resource))
        if quota is None:
            return False
        return quota.used + amount <= quota.limit

    def get_quota(self, installation_id: str, resource: str) -> Quota:
        return self._get(installation_id, resource)

    def list_quotas(self, installation_id: str) -> list[Quota]:
        return [q for (inst, _), q in self._quotas.items() if inst == installation_id]

    def reset_usage(self, installation_id: str, resource: str) -> Quota:
        quota = self._get(installation_id, resource)
        quota.used = 0.0
        return quota

    def _get(self, installation_id: str, resource: str) -> Quota:
        key = (installation_id, resource)
        quota = self._quotas.get(key)
        if quota is None:
            raise KeyError(f"No quota for resource {resource}")
        return quota
