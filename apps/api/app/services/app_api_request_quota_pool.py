"""App API Request Quota Pool — shared quota pools across consumers.

Manages shared quota pools:
- Create pools with total capacity
- Allocate quotas to consumers from pool
- Track pool-level utilization
- Per-installation scoped pools
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class QuotaPool:
    """A shared request quota pool."""

    pool_id: str
    name: str
    total_capacity: int
    allocated: int = 0
    consumed: int = 0

    @property
    def available(self) -> int:
        return max(0, self.total_capacity - self.allocated)

    @property
    def utilization_pct(self) -> float:
        if self.total_capacity == 0:
            return 0.0
        return round(self.consumed / self.total_capacity * 100, 1)


class AppAPIRequestQuotaPool:
    """Shared quota pools across consumers."""

    def __init__(self) -> None:
        self._pools: dict[tuple[str, str], QuotaPool] = {}
        self._allocations: dict[tuple[str, str, str], int] = {}  # (inst, pool, consumer) → amount

    def create_pool(
        self, installation_id: str, pool_id: str, name: str, total_capacity: int,
    ) -> QuotaPool:
        if not installation_id:
            raise ValueError("installation_id is required")
        if total_capacity < 1:
            raise ValueError("total_capacity must be at least 1")
        pool = QuotaPool(pool_id=pool_id, name=name, total_capacity=total_capacity)
        self._pools[(installation_id, pool_id)] = pool
        return pool

    def allocate(
        self, installation_id: str, pool_id: str, consumer_id: str, amount: int,
    ) -> int:
        """Allocate quota from pool. Returns allocated amount."""
        pool = self._get(installation_id, pool_id)
        actual = min(amount, pool.available)
        if actual <= 0:
            raise ValueError("No capacity available")
        pool.allocated += actual
        key = (installation_id, pool_id, consumer_id)
        self._allocations[key] = self._allocations.get(key, 0) + actual
        return actual

    def consume(self, installation_id: str, pool_id: str, amount: int = 1) -> QuotaPool:
        pool = self._get(installation_id, pool_id)
        pool.consumed += amount
        return pool

    def get_pool(self, installation_id: str, pool_id: str) -> QuotaPool:
        return self._get(installation_id, pool_id)

    def list_pools(self, installation_id: str) -> list[QuotaPool]:
        return [p for (inst, _), p in self._pools.items() if inst == installation_id]

    def _get(self, installation_id: str, pool_id: str) -> QuotaPool:
        key = (installation_id, pool_id)
        p = self._pools.get(key)
        if p is None:
            raise KeyError(f"Pool {pool_id} not found")
        return p
