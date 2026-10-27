"""Connection Pool Manager — manage multiple named pools with monitoring.

Implements:
- Named connection pools with independent configuration
- Connection lifecycle: create → checkout → use → checkin → destroy
- Health check on checkout (test-on-borrow)
- Pool warmup (pre-create connections)
- Stale connection detection and replacement
- Cross-pool metrics dashboard
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class PoolConnection:
    conn_id: str
    pool_name: str
    created_at: float
    last_used: float = 0.0
    last_health_check: float = 0.0
    healthy: bool = True
    in_use: bool = False
    use_count: int = 0


@dataclass
class PoolConfig:
    name: str
    min_size: int = 2
    max_size: int = 10
    max_idle_seconds: float = 300
    health_check_interval: float = 30
    max_lifetime_seconds: float = 3600


class ConnPoolManagerService:
    def __init__(self):
        self._pools: dict[str, list[PoolConnection]] = {}
        self._configs: dict[str, PoolConfig] = {}
        self._counter = 0
        self._total_checkouts = 0
        self._total_errors = 0

    def create_pool(self, config: PoolConfig) -> int:
        """Create and warm up a pool. Returns connections created."""
        self._configs[config.name] = config
        self._pools[config.name] = []
        for _ in range(config.min_size):
            self._create_connection(config.name)
        return config.min_size

    def _create_connection(self, pool_name: str) -> PoolConnection:
        self._counter += 1
        now = time.time()
        conn = PoolConnection(conn_id=f"conn-{self._counter}",
                              pool_name=pool_name, created_at=now,
                              last_health_check=now)
        self._pools[pool_name].append(conn)
        return conn

    def checkout(self, pool_name: str) -> PoolConnection | None:
        """Get a connection from the pool."""
        pool = self._pools.get(pool_name)
        config = self._configs.get(pool_name)
        if not pool or not config:
            return None

        now = time.time()
        self._total_checkouts += 1

        # Find available healthy connection
        for conn in pool:
            if conn.in_use or not conn.healthy:
                continue
            # Stale check
            if conn.last_used > 0 and (now - conn.last_used) > config.max_idle_seconds:
                conn.healthy = False
                continue
            # Lifetime check
            if (now - conn.created_at) > config.max_lifetime_seconds:
                conn.healthy = False
                continue
            # Health check interval
            if (now - conn.last_health_check) > config.health_check_interval:
                conn.last_health_check = now  # simulate health check pass

            conn.in_use = True
            conn.last_used = now
            conn.use_count += 1
            return conn

        # No available connections — grow if possible
        if len(pool) < config.max_size:
            conn = self._create_connection(pool_name)
            conn.in_use = True
            conn.last_used = now
            conn.use_count += 1
            return conn

        return None  # pool exhausted

    def checkin(self, conn_id: str, healthy: bool = True) -> bool:
        """Return a connection to its pool."""
        for pool in self._pools.values():
            for conn in pool:
                if conn.conn_id == conn_id and conn.in_use:
                    conn.in_use = False
                    conn.healthy = healthy
                    conn.last_used = time.time()
                    if not healthy:
                        self._total_errors += 1
                    return True
        return False

    def cleanup(self, pool_name: str) -> int:
        """Remove unhealthy/stale connections, maintain min_size."""
        pool = self._pools.get(pool_name, [])
        config = self._configs.get(pool_name)
        if not config:
            return 0

        now = time.time()
        to_remove = []
        for conn in pool:
            if conn.in_use:
                continue
            if not conn.healthy:
                to_remove.append(conn)
            elif (now - conn.created_at) > config.max_lifetime_seconds:
                to_remove.append(conn)

        removed = 0
        for conn in to_remove:
            if len(pool) - removed > config.min_size:
                pool.remove(conn)
                removed += 1

        # Replenish to min_size
        while len(pool) < config.min_size:
            self._create_connection(pool_name)

        return removed

    def get_pool_stats(self, pool_name: str) -> dict:
        pool = self._pools.get(pool_name, [])
        active = sum(1 for c in pool if c.in_use)
        idle = sum(1 for c in pool if not c.in_use and c.healthy)
        unhealthy = sum(1 for c in pool if not c.healthy)
        return {"total": len(pool), "active": active, "idle": idle,
                "unhealthy": unhealthy}

    def get_dashboard(self) -> dict:
        pools = {}
        for name in self._pools:
            pools[name] = self.get_pool_stats(name)
        return {"pools": pools, "total_checkouts": self._total_checkouts,
                "total_errors": self._total_errors}
