"""API Quota Allocator — distributed quota management across org teams and apps.

Manages hierarchical quota allocation for the developer platform:
- Org-level quota pool with sub-allocation to teams/apps
- Quota types: requests, bandwidth, storage, compute
- Reservation-based allocation (reserve → use → release)
- Over-commit protection with configurable headroom
- Quota transfer between sub-allocations
- Usage-to-allocation ratio tracking
- Automatic reclaim of unused reservations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum

import structlog

log = structlog.get_logger()


class QuotaType(str, Enum):
    REQUESTS = "requests"
    BANDWIDTH_MB = "bandwidth_mb"
    STORAGE_MB = "storage_mb"
    COMPUTE_SECONDS = "compute_seconds"


@dataclass
class QuotaPool:
    """Top-level org quota pool."""

    org_id: str
    quota_type: QuotaType
    total: int                    # total capacity
    reserved: int = 0             # sum of all sub-allocations
    used: int = 0                 # actual consumption across all subs

    @property
    def available(self) -> int:
        return max(0, self.total - self.reserved)

    @property
    def utilization_pct(self) -> float:
        return (self.used / self.total * 100) if self.total > 0 else 0.0


@dataclass
class SubAllocation:
    """A quota slice allocated to a team or app."""

    alloc_id: str
    pool_key: tuple[str, QuotaType]   # (org_id, quota_type)
    entity_id: str                     # team_id or app_id
    entity_type: str                   # "team" or "app"
    reserved: int                      # allocated amount
    used: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_used_at: datetime | None = None

    @property
    def remaining(self) -> int:
        return max(0, self.reserved - self.used)

    @property
    def usage_pct(self) -> float:
        return (self.used / self.reserved * 100) if self.reserved > 0 else 0.0


@dataclass
class AllocationResult:
    """Result of an allocation attempt."""

    success: bool
    alloc_id: str | None = None
    error: str | None = None
    remaining_pool: int = 0


@dataclass
class ConsumeResult:
    """Result of consuming quota."""

    allowed: bool
    remaining: int = 0
    over_limit: bool = False
    error: str | None = None


@dataclass
class PoolSummary:
    """Summary of a quota pool's allocations."""

    org_id: str
    quota_type: str
    total: int
    reserved: int
    used: int
    available: int
    utilization_pct: float
    allocations: list[dict]


class ApiQuotaAllocator:
    """Hierarchical quota allocation with reservation semantics."""

    def __init__(self, headroom_pct: float = 5.0):
        """headroom_pct: percentage of pool kept unallocatable as safety margin."""
        self._headroom_pct = headroom_pct
        # (org_id, quota_type) → QuotaPool
        self._pools: dict[tuple[str, QuotaType], QuotaPool] = {}
        # alloc_id → SubAllocation
        self._allocations: dict[str, SubAllocation] = {}
        self._next_id = 0

    # ── Pool management ──────────────────────────────────

    def create_pool(self, org_id: str, quota_type: QuotaType, total: int) -> QuotaPool:
        """Create or update an org quota pool."""
        key = (org_id, quota_type)
        pool = QuotaPool(org_id=org_id, quota_type=quota_type, total=total)
        self._pools[key] = pool
        return pool

    def get_pool(self, org_id: str, quota_type: QuotaType) -> QuotaPool | None:
        return self._pools.get((org_id, quota_type))

    def resize_pool(self, org_id: str, quota_type: QuotaType, new_total: int) -> QuotaPool:
        """Resize a pool. Fails if new_total < currently reserved."""
        key = (org_id, quota_type)
        pool = self._pools.get(key)
        if pool is None:
            raise ValueError(f"Pool not found: {org_id}/{quota_type.value}")
        if new_total < pool.reserved:
            raise ValueError(
                f"Cannot shrink below reserved ({pool.reserved}): requested {new_total}"
            )
        pool.total = new_total
        return pool

    # ── Allocation ───────────────────────────────────────

    def allocate(self, org_id: str, quota_type: QuotaType,
                 entity_id: str, entity_type: str, amount: int) -> AllocationResult:
        """Reserve a quota slice for a team or app."""
        key = (org_id, quota_type)
        pool = self._pools.get(key)
        if pool is None:
            return AllocationResult(success=False, error="Pool not found")

        # Headroom check
        allocatable = int(pool.total * (1 - self._headroom_pct / 100))
        available = allocatable - pool.reserved
        if amount > available:
            return AllocationResult(
                success=False,
                error=f"Insufficient quota: requested {amount}, available {available} "
                      f"(headroom {self._headroom_pct}%)",
                remaining_pool=available,
            )

        self._next_id += 1
        alloc_id = f"alloc-{self._next_id}"
        alloc = SubAllocation(
            alloc_id=alloc_id,
            pool_key=key,
            entity_id=entity_id,
            entity_type=entity_type,
            reserved=amount,
        )
        self._allocations[alloc_id] = alloc
        pool.reserved += amount

        log.info("quota.allocated", alloc_id=alloc_id, entity=entity_id, amount=amount)
        return AllocationResult(success=True, alloc_id=alloc_id, remaining_pool=available - amount)

    def release(self, alloc_id: str) -> bool:
        """Release a sub-allocation back to the pool."""
        alloc = self._allocations.pop(alloc_id, None)
        if alloc is None:
            return False
        pool = self._pools.get(alloc.pool_key)
        if pool:
            pool.reserved -= alloc.reserved
            pool.used -= alloc.used  # remove consumed from pool tracking
        log.info("quota.released", alloc_id=alloc_id)
        return True

    def transfer(self, from_alloc_id: str, to_alloc_id: str, amount: int) -> bool:
        """Transfer quota between two sub-allocations in the same pool."""
        src = self._allocations.get(from_alloc_id)
        dst = self._allocations.get(to_alloc_id)
        if src is None or dst is None:
            return False
        if src.pool_key != dst.pool_key:
            return False
        if amount > src.remaining:
            return False
        src.reserved -= amount
        dst.reserved += amount
        log.info("quota.transferred", from_id=from_alloc_id, to_id=to_alloc_id, amount=amount)
        return True

    # ── Consumption ──────────────────────────────────────

    def consume(self, alloc_id: str, amount: int) -> ConsumeResult:
        """Consume quota from a sub-allocation."""
        alloc = self._allocations.get(alloc_id)
        if alloc is None:
            return ConsumeResult(allowed=False, error="Allocation not found")

        if alloc.used + amount > alloc.reserved:
            return ConsumeResult(
                allowed=False,
                remaining=alloc.remaining,
                over_limit=True,
                error=f"Would exceed allocation: {alloc.used + amount} > {alloc.reserved}",
            )

        alloc.used += amount
        alloc.last_used_at = datetime.now(UTC)

        # Update pool-level tracking
        pool = self._pools.get(alloc.pool_key)
        if pool:
            pool.used += amount

        return ConsumeResult(allowed=True, remaining=alloc.remaining)

    # ── Reclaim ──────────────────────────────────────────

    def reclaim_unused(self, idle_hours: int = 24) -> list[str]:
        """Release allocations that haven't been used within idle_hours."""
        cutoff = datetime.now(UTC) - timedelta(hours=idle_hours)
        reclaimed: list[str] = []
        for alloc_id in list(self._allocations.keys()):
            alloc = self._allocations[alloc_id]
            if alloc.used == 0 and alloc.created_at < cutoff:
                self.release(alloc_id)
                reclaimed.append(alloc_id)
            elif alloc.last_used_at and alloc.last_used_at < cutoff and alloc.usage_pct < 10:
                self.release(alloc_id)
                reclaimed.append(alloc_id)
        return reclaimed

    # ── Queries ──────────────────────────────────────────

    def get_allocation(self, alloc_id: str) -> SubAllocation | None:
        return self._allocations.get(alloc_id)

    def get_entity_allocations(self, entity_id: str) -> list[SubAllocation]:
        return sorted(
            [a for a in self._allocations.values() if a.entity_id == entity_id],
            key=lambda a: a.alloc_id,
        )

    def get_pool_summary(self, org_id: str, quota_type: QuotaType) -> PoolSummary | None:
        pool = self._pools.get((org_id, quota_type))
        if pool is None:
            return None
        allocs = [
            a for a in self._allocations.values()
            if a.pool_key == (org_id, quota_type)
        ]
        return PoolSummary(
            org_id=org_id,
            quota_type=quota_type.value,
            total=pool.total,
            reserved=pool.reserved,
            used=pool.used,
            available=pool.available,
            utilization_pct=round(pool.utilization_pct, 2),
            allocations=[
                {
                    "alloc_id": a.alloc_id,
                    "entity_id": a.entity_id,
                    "entity_type": a.entity_type,
                    "reserved": a.reserved,
                    "used": a.used,
                    "usage_pct": round(a.usage_pct, 2),
                }
                for a in sorted(allocs, key=lambda x: x.used, reverse=True)
            ],
        )
