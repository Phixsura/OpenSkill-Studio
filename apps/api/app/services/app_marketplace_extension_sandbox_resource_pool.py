"""Sandbox Resource Pool — manage shared resource pools for sandboxes.

Allocates and reclaims compute resources (CPU cores, memory slots,
GPU shares) from a fixed pool with fairness, priority queuing,
and reservation support.
"""
from __future__ import annotations
import secrets
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


class ResourceKind(str, Enum):
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    DISK_IO = "disk_io"


class AllocationStatus(str, Enum):
    ACTIVE = "active"
    QUEUED = "queued"
    RELEASED = "released"
    EXPIRED = "expired"


@dataclass
class ResourceAllocation:
    allocation_id: str
    sandbox_id: str
    resource: ResourceKind
    amount: float
    priority: int = 0
    status: AllocationStatus = AllocationStatus.ACTIVE


@dataclass
class PoolConfig:
    resource: ResourceKind
    total_capacity: float
    allocated: float = 0.0
    reserved: float = 0.0

    @property
    def available(self) -> float:
        return max(0, self.total_capacity - self.allocated - self.reserved)

    @property
    def utilization_pct(self) -> float:
        return round(self.allocated / self.total_capacity * 100, 1) if self.total_capacity else 0


class ResourcePoolService:
    """Manages shared resource pools with allocation and queueing."""

    def __init__(self):
        self._pools: dict[ResourceKind, PoolConfig] = {}
        self._allocations: dict[str, ResourceAllocation] = {}
        self._queue: list[ResourceAllocation] = []

    def configure_pool(self, resource: ResourceKind, capacity: float) -> PoolConfig:
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        pool = PoolConfig(resource=resource, total_capacity=capacity)
        self._pools[resource] = pool
        return pool

    def allocate(self, sandbox_id: str, resource: ResourceKind,
                 amount: float, priority: int = 0) -> ResourceAllocation:
        pool = self._pools.get(resource)
        if not pool:
            raise ValueError(f"No pool for {resource.value}")
        if amount <= 0:
            raise ValueError("Amount must be positive")

        alloc_id = f"alloc_{secrets.token_urlsafe(8)}"
        alloc = ResourceAllocation(
            allocation_id=alloc_id, sandbox_id=sandbox_id,
            resource=resource, amount=amount, priority=priority,
        )

        if pool.available >= amount:
            pool.allocated += amount
            alloc.status = AllocationStatus.ACTIVE
        else:
            alloc.status = AllocationStatus.QUEUED
            self._queue.append(alloc)
            self._queue.sort(key=lambda a: -a.priority)

        self._allocations[alloc_id] = alloc
        return alloc

    def release(self, allocation_id: str) -> bool:
        alloc = self._allocations.get(allocation_id)
        if not alloc or alloc.status == AllocationStatus.RELEASED:
            return False

        if alloc.status == AllocationStatus.ACTIVE:
            pool = self._pools.get(alloc.resource)
            if pool:
                pool.allocated = max(0, pool.allocated - alloc.amount)
            # Try to fulfill queued allocations
            self._process_queue(alloc.resource)

        elif alloc.status == AllocationStatus.QUEUED:
            self._queue = [a for a in self._queue if a.allocation_id != allocation_id]

        alloc.status = AllocationStatus.RELEASED
        return True

    def _process_queue(self, resource: ResourceKind) -> int:
        pool = self._pools.get(resource)
        if not pool:
            return 0
        fulfilled = 0
        remaining = []
        for alloc in self._queue:
            if alloc.resource != resource:
                remaining.append(alloc)
                continue
            if pool.available >= alloc.amount:
                pool.allocated += alloc.amount
                alloc.status = AllocationStatus.ACTIVE
                fulfilled += 1
            else:
                remaining.append(alloc)
        self._queue = remaining
        return fulfilled

    def reserve(self, resource: ResourceKind, amount: float) -> bool:
        pool = self._pools.get(resource)
        if not pool or pool.available < amount:
            return False
        pool.reserved += amount
        return True

    def get_pool_status(self, resource: ResourceKind) -> dict | None:
        pool = self._pools.get(resource)
        if not pool:
            return None
        return {
            "resource": resource.value,
            "total": pool.total_capacity,
            "allocated": pool.allocated,
            "reserved": pool.reserved,
            "available": pool.available,
            "utilization_pct": pool.utilization_pct,
            "queued": sum(1 for a in self._queue if a.resource == resource),
        }

    def get_sandbox_allocations(self, sandbox_id: str) -> list[ResourceAllocation]:
        return [a for a in self._allocations.values()
                if a.sandbox_id == sandbox_id and a.status == AllocationStatus.ACTIVE]
