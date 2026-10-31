"""Consumer API Connection Pool — connection pool management with health monitoring."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class Connection:
    conn_id: str
    pool_id: str
    status: str = "idle"  # idle, active, closed
    created_at: float = 0.0
    last_used_at: float = 0.0
    request_count: int = 0


@dataclass
class Pool:
    pool_id: str
    name: str
    max_size: int = 20
    min_size: int = 2
    idle_timeout_ms: int = 30000
    connections: dict[str, Connection] = field(default_factory=dict)


@dataclass
class ConnectionPoolManager:
    """Manage connection pools with health monitoring."""

    _pools: dict[str, Pool] = field(default_factory=dict)
    _conn_counter: int = 0

    def create_pool(self, pool_id: str, name: str, max_size: int = 20,
                    min_size: int = 2) -> dict:
        if pool_id in self._pools:
            raise ValueError(f"Pool {pool_id} already exists")
        if max_size < 1:
            raise ValueError("max_size must be positive")
        if min_size > max_size:
            raise ValueError("min_size cannot exceed max_size")
        pool = Pool(pool_id=pool_id, name=name, max_size=max_size, min_size=min_size)
        # Pre-create min connections
        for _ in range(min_size):
            self._conn_counter += 1
            cid = f"conn-{self._conn_counter}"
            pool.connections[cid] = Connection(conn_id=cid, pool_id=pool_id)
        self._pools[pool_id] = pool
        logger.info("pool_created", pool_id=pool_id, size=min_size)
        return {"pool_id": pool_id, "initial_connections": min_size}

    def acquire(self, pool_id: str) -> dict:
        pool = self._pools.get(pool_id)
        if not pool:
            raise ValueError(f"Pool {pool_id} not found")
        # Find idle connection
        for conn in pool.connections.values():
            if conn.status == "idle":
                conn.status = "active"
                conn.request_count += 1
                return {"conn_id": conn.conn_id, "acquired": True}
        # Create new if under max
        if len(pool.connections) < pool.max_size:
            self._conn_counter += 1
            cid = f"conn-{self._conn_counter}"
            conn = Connection(conn_id=cid, pool_id=pool_id, status="active", request_count=1)
            pool.connections[cid] = conn
            return {"conn_id": cid, "acquired": True, "new_connection": True}
        return {"acquired": False, "reason": "pool_exhausted"}

    def release(self, pool_id: str, conn_id: str) -> dict:
        pool = self._pools.get(pool_id)
        if not pool:
            raise ValueError(f"Pool {pool_id} not found")
        conn = pool.connections.get(conn_id)
        if not conn:
            return {"released": False, "reason": "not_found"}
        conn.status = "idle"
        return {"conn_id": conn_id, "released": True}

    def close_connection(self, pool_id: str, conn_id: str) -> dict:
        pool = self._pools.get(pool_id)
        if not pool:
            raise ValueError(f"Pool {pool_id} not found")
        conn = pool.connections.pop(conn_id, None)
        if conn:
            return {"closed": True, "remaining": len(pool.connections)}
        return {"closed": False}

    def get_pool_status(self, pool_id: str) -> dict:
        pool = self._pools.get(pool_id)
        if not pool:
            return {"error": "not_found"}
        conns = list(pool.connections.values())
        active = sum(1 for c in conns if c.status == "active")
        idle = sum(1 for c in conns if c.status == "idle")
        return {
            "pool_id": pool.pool_id, "name": pool.name,
            "total": len(conns), "active": active, "idle": idle,
            "max_size": pool.max_size, "min_size": pool.min_size,
            "utilization_pct": round(active / pool.max_size * 100, 1),
        }

    def list_pools(self) -> list[dict]:
        return [self.get_pool_status(pid) for pid in sorted(self._pools)]

    def get_stats(self) -> dict:
        total_conns = sum(len(p.connections) for p in self._pools.values())
        total_active = sum(
            sum(1 for c in p.connections.values() if c.status == "active")
            for p in self._pools.values()
        )
        return {
            "total_pools": len(self._pools),
            "total_connections": total_conns,
            "total_active": total_active,
            "total_idle": total_conns - total_active,
        }
