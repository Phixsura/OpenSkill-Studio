"""App Connection Pool — manage database connection pools for installed apps.

Tracks connection pool status and metrics:
- Pool size and active connections
- Wait queue depth
- Connection acquisition timing
- Per-installation scoped pools
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class PoolStatus:
    """Current connection pool status."""

    pool_id: str
    max_size: int
    active: int
    idle: int
    waiting: int
    total_acquired: int = 0
    total_timeouts: int = 0
    avg_acquire_ms: float = 0.0


class AppConnectionPool:
    """Manage database connection pools."""

    def __init__(self) -> None:
        self._pools: dict[tuple[str, str], PoolStatus] = {}

    def register_pool(
        self,
        installation_id: str,
        pool_id: str,
        max_size: int,
    ) -> PoolStatus:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not pool_id:
            raise ValueError("pool_id is required")
        if max_size < 1:
            raise ValueError("max_size must be >= 1")

        status = PoolStatus(pool_id=pool_id, max_size=max_size, active=0, idle=max_size, waiting=0)
        self._pools[(installation_id, pool_id)] = status
        return status

    def update_status(
        self,
        installation_id: str,
        pool_id: str,
        active: int,
        idle: int,
        waiting: int,
        avg_acquire_ms: float = 0.0,
    ) -> PoolStatus:
        status = self._get(installation_id, pool_id)
        status.active = max(0, active)
        status.idle = max(0, idle)
        status.waiting = max(0, waiting)
        status.avg_acquire_ms = max(0.0, avg_acquire_ms)
        return status

    def record_acquisition(
        self, installation_id: str, pool_id: str, timed_out: bool = False
    ) -> PoolStatus:
        status = self._get(installation_id, pool_id)
        status.total_acquired += 1
        if timed_out:
            status.total_timeouts += 1
        return status

    def is_saturated(self, installation_id: str, pool_id: str) -> bool:
        """Check if pool is at capacity with waiters."""
        status = self._get(installation_id, pool_id)
        return status.active >= status.max_size and status.waiting > 0

    def utilization_pct(self, installation_id: str, pool_id: str) -> float:
        status = self._get(installation_id, pool_id)
        return round(status.active / status.max_size * 100, 1) if status.max_size > 0 else 0

    def get_pool(self, installation_id: str, pool_id: str) -> PoolStatus:
        return self._get(installation_id, pool_id)

    def list_pools(self, installation_id: str) -> list[PoolStatus]:
        return [p for (inst, _), p in self._pools.items() if inst == installation_id]

    def _get(self, installation_id: str, pool_id: str) -> PoolStatus:
        key = (installation_id, pool_id)
        p = self._pools.get(key)
        if p is None:
            raise KeyError(f"Pool {pool_id} not found")
        return p
