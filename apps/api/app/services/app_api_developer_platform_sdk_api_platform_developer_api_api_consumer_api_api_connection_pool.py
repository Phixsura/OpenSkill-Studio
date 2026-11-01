"""API Consumer Connection Pool — manage persistent connection pools per consumer."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ConnectionPool:
    consumer_id: str
    max_connections: int = 100
    active_connections: int = 0
    idle_connections: int = 0
    total_created: int = 0
    total_reused: int = 0
    total_exhausted: int = 0

    @property
    def utilization_pct(self) -> float:
        if self.max_connections == 0: return 0.0
        return round((self.active_connections / self.max_connections) * 100, 1)

    @property
    def reuse_rate(self) -> float:
        total = self.total_created + self.total_reused
        if total == 0: return 0.0
        return round((self.total_reused / total) * 100, 1)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConnectionPool:
    def __init__(self) -> None:
        self._pools: dict[tuple[str, str], ConnectionPool] = {}

    def create_pool(self, installation_id: str, consumer_id: str, max_connections: int = 100) -> ConnectionPool:
        if not installation_id: raise ValueError("installation_id is required")
        if max_connections < 1: raise ValueError("max_connections must be >= 1")
        pool = ConnectionPool(consumer_id=consumer_id, max_connections=max_connections)
        self._pools[(installation_id, consumer_id)] = pool
        return pool

    def acquire(self, installation_id: str, consumer_id: str) -> bool:
        pool = self._pools.get((installation_id, consumer_id))
        if pool is None: return True  # no pool = no limit
        if pool.idle_connections > 0:
            pool.idle_connections -= 1
            pool.active_connections += 1
            pool.total_reused += 1
            return True
        if pool.active_connections >= pool.max_connections:
            pool.total_exhausted += 1
            return False
        pool.active_connections += 1
        pool.total_created += 1
        return True

    def release(self, installation_id: str, consumer_id: str) -> None:
        pool = self._pools.get((installation_id, consumer_id))
        if pool and pool.active_connections > 0:
            pool.active_connections -= 1
            pool.idle_connections += 1

    def get_pool(self, installation_id: str, consumer_id: str) -> ConnectionPool | None:
        return self._pools.get((installation_id, consumer_id))

    def list_pools(self, installation_id: str) -> list[ConnectionPool]:
        return [p for (inst, _), p in self._pools.items() if inst == installation_id]
