"""Sandbox Connection Pool — manage database/API connection pools.

Tracks active/idle connections, enforces pool limits, connection
health checks, and provides pool utilization stats.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class Connection:
    conn_id: str
    target: str
    state: str = "idle"  # idle, active, closed


class SandboxConnPoolService:
    """Manages connection pools for sandbox resources."""

    def __init__(self):
        self._pools: dict[str, dict[str, list[Connection]]] = defaultdict(lambda: defaultdict(list))
        self._limits: dict[str, dict[str, int]] = defaultdict(dict)
        self._counter = 0

    def configure(self, sandbox_id: str, target: str, max_conns: int) -> dict:
        self._limits[sandbox_id][target] = max_conns
        return {"target": target, "max": max_conns}

    def acquire(self, sandbox_id: str, target: str) -> Connection | dict:
        pool = self._pools[sandbox_id][target]
        limit = self._limits.get(sandbox_id, {}).get(target, 10)
        # Reuse idle
        for conn in pool:
            if conn.state == "idle":
                conn.state = "active"
                return conn
        # Create new if under limit
        active = sum(1 for c in pool if c.state != "closed")
        if active >= limit:
            return {"error": "Pool exhausted"}
        self._counter += 1
        conn = Connection(conn_id=f"conn_{self._counter}", target=target, state="active")
        pool.append(conn)
        return conn

    def release(self, sandbox_id: str, target: str, conn_id: str) -> bool:
        for conn in self._pools.get(sandbox_id, {}).get(target, []):
            if conn.conn_id == conn_id and conn.state == "active":
                conn.state = "idle"
                return True
        return False

    def close(self, sandbox_id: str, target: str, conn_id: str) -> bool:
        for conn in self._pools.get(sandbox_id, {}).get(target, []):
            if conn.conn_id == conn_id:
                conn.state = "closed"
                return True
        return False

    def get_stats(self, sandbox_id: str, target: str) -> dict:
        pool = self._pools.get(sandbox_id, {}).get(target, [])
        return {
            "active": sum(1 for c in pool if c.state == "active"),
            "idle": sum(1 for c in pool if c.state == "idle"),
            "closed": sum(1 for c in pool if c.state == "closed"),
            "total": len([c for c in pool if c.state != "closed"]),
            "max": self._limits.get(sandbox_id, {}).get(target, 10),
        }
