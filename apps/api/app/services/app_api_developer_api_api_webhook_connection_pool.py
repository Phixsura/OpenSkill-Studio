"""App API Developer Webhook Connection Pool — manage persistent HTTP connections."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ConnectionPoolStats:
    destination: str
    max_connections: int
    active_connections: int = 0
    idle_connections: int = 0
    total_requests_served: int = 0
    connection_errors: int = 0

    @property
    def utilization_pct(self) -> float:
        return round(self.active_connections / self.max_connections * 100, 1) if self.max_connections > 0 else 0.0

    @property
    def healthy(self) -> bool:
        return self.utilization_pct < 90 and self.connection_errors == 0

class AppAPIDeveloperAPIApiWebhookConnectionPool:
    def __init__(self) -> None:
        self._pools: dict[tuple[str, str], ConnectionPoolStats] = {}

    def configure(self, installation_id: str, destination: str, max_connections: int) -> ConnectionPoolStats:
        if not installation_id: raise ValueError("installation_id is required")
        if max_connections < 1: raise ValueError("max_connections must be >= 1")
        key = (installation_id, destination)
        p = ConnectionPoolStats(destination=destination, max_connections=max_connections)
        self._pools[key] = p
        return p

    def update(self, installation_id: str, destination: str, active: int, idle: int, requests_served: int = 0, errors: int = 0) -> ConnectionPoolStats:
        key = (installation_id, destination)
        p = self._pools.get(key)
        if p is None: raise KeyError(f"No pool for {destination}")
        p.active_connections = active
        p.idle_connections = idle
        p.total_requests_served += requests_served
        p.connection_errors += errors
        return p

    def all_pools(self, installation_id: str) -> list[ConnectionPoolStats]:
        return [p for (inst, _), p in self._pools.items() if inst == installation_id]

    def unhealthy(self, installation_id: str) -> list[ConnectionPoolStats]:
        return [p for p in self.all_pools(installation_id) if not p.healthy]

    def total_active(self, installation_id: str) -> int:
        return sum(p.active_connections for p in self.all_pools(installation_id))
