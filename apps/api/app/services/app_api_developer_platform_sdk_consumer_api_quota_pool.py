"""Consumer Quota Pool — shared quota pools with reservation and release."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class QuotaPool:
    pool_id: str
    name: str
    total_capacity: int
    reserved: int = 0
    used: int = 0


@dataclass
class Reservation:
    reservation_id: str
    pool_id: str
    consumer_id: str
    amount: int
    status: str = "active"  # active, released, expired


@dataclass
class QuotaPoolManager:
    """Manage shared quota pools with reservation semantics."""

    _pools: dict[str, QuotaPool] = field(default_factory=dict)
    _reservations: dict[str, Reservation] = field(default_factory=dict)

    def create_pool(self, pool_id: str, name: str, capacity: int) -> dict:
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        if pool_id in self._pools:
            raise ValueError(f"Pool {pool_id} already exists")
        self._pools[pool_id] = QuotaPool(pool_id=pool_id, name=name, total_capacity=capacity)
        logger.info("quota_pool_created", pool_id=pool_id, capacity=capacity)
        return {"pool_id": pool_id, "capacity": capacity}

    def reserve(self, reservation_id: str, pool_id: str, consumer_id: str, amount: int) -> dict:
        pool = self._pools.get(pool_id)
        if not pool:
            raise ValueError(f"Pool {pool_id} not found")
        if amount <= 0:
            raise ValueError("Amount must be positive")
        available = pool.total_capacity - pool.reserved - pool.used
        if amount > available:
            return {"success": False, "reason": "insufficient_capacity",
                    "available": available, "requested": amount}
        pool.reserved += amount
        self._reservations[reservation_id] = Reservation(
            reservation_id=reservation_id, pool_id=pool_id,
            consumer_id=consumer_id, amount=amount,
        )
        logger.info("quota_reserved", reservation_id=reservation_id, amount=amount)
        return {"success": True, "reservation_id": reservation_id, "amount": amount}

    def consume(self, reservation_id: str, amount: int | None = None) -> dict:
        res = self._reservations.get(reservation_id)
        if not res or res.status != "active":
            raise ValueError(f"Reservation {reservation_id} not found or inactive")
        pool = self._pools.get(res.pool_id)
        if not pool:
            raise ValueError("Pool not found")
        actual = amount if amount is not None else res.amount
        if actual > res.amount:
            raise ValueError("Cannot consume more than reserved")
        pool.reserved -= res.amount
        pool.used += actual
        res.status = "released"
        return {"consumed": actual, "pool_used": pool.used}

    def release(self, reservation_id: str) -> dict:
        res = self._reservations.get(reservation_id)
        if not res or res.status != "active":
            return {"released": False, "reason": "not_active"}
        pool = self._pools.get(res.pool_id)
        if pool:
            pool.reserved -= res.amount
        res.status = "released"
        logger.info("quota_released", reservation_id=reservation_id)
        return {"released": True, "amount": res.amount}

    def get_pool_status(self, pool_id: str) -> dict:
        pool = self._pools.get(pool_id)
        if not pool:
            return {"error": "not_found"}
        available = pool.total_capacity - pool.reserved - pool.used
        return {
            "pool_id": pool.pool_id,
            "name": pool.name,
            "total_capacity": pool.total_capacity,
            "reserved": pool.reserved,
            "used": pool.used,
            "available": available,
            "utilization_pct": round((pool.used + pool.reserved) / pool.total_capacity * 100, 1),
        }

    def list_pools(self) -> list[dict]:
        return [self.get_pool_status(pid) for pid in sorted(self._pools)]

    def get_consumer_reservations(self, consumer_id: str) -> list[dict]:
        return [
            {"reservation_id": r.reservation_id, "pool_id": r.pool_id,
             "amount": r.amount, "status": r.status}
            for r in self._reservations.values()
            if r.consumer_id == consumer_id
        ]
