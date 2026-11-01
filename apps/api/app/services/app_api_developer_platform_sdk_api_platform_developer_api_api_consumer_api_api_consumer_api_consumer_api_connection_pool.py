"""Consumer API Connection Pool — manage per-consumer connection limits and pooling."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
import structlog

log = structlog.get_logger()

@dataclass
class PoolConfig:
    consumer_id: str
    max_connections: int = 100
    idle_timeout_seconds: int = 300
    max_lifetime_seconds: int = 3600

@dataclass
class Connection:
    connection_id: str
    consumer_id: str
    state: str = "active"  # "active", "idle", "closed"
    created_at: datetime | None = None
    last_used_at: datetime | None = None

@dataclass
class PoolStats:
    consumer_id: str
    active: int
    idle: int
    total: int
    max_connections: int
    utilization_pct: float

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiConnectionPool:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], PoolConfig] = {}
        self._connections: dict[tuple[str, str], list[Connection]] = {}

    def configure(self, installation_id: str, config: PoolConfig) -> PoolConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if config.max_connections < 1:
            raise ValueError("max_connections must be positive")
        self._configs[(installation_id, config.consumer_id)] = config
        return config

    def acquire(self, installation_id: str, consumer_id: str, connection_id: str, now: datetime) -> Connection:
        key = (installation_id, consumer_id)
        config = self._configs.get(key, PoolConfig(consumer_id=consumer_id))
        if key not in self._connections:
            self._connections[key] = []
        conns = self._connections[key]
        active = [c for c in conns if c.state != "closed"]
        if len(active) >= config.max_connections:
            # Try to close an idle one
            idle = [c for c in conns if c.state == "idle"]
            if idle:
                idle[0].state = "closed"
            else:
                raise ValueError("Connection pool exhausted")
        conn = Connection(connection_id=connection_id, consumer_id=consumer_id, state="active", created_at=now, last_used_at=now)
        conns.append(conn)
        return conn

    def release(self, installation_id: str, consumer_id: str, connection_id: str, now: datetime) -> Connection:
        conns = self._connections.get((installation_id, consumer_id), [])
        for c in conns:
            if c.connection_id == connection_id and c.state == "active":
                c.state = "idle"
                c.last_used_at = now
                return c
        raise ValueError("Connection not found or not active")

    def cleanup(self, installation_id: str, consumer_id: str, now: datetime) -> int:
        key = (installation_id, consumer_id)
        config = self._configs.get(key, PoolConfig(consumer_id=consumer_id))
        conns = self._connections.get(key, [])
        closed = 0
        for c in conns:
            if c.state == "idle" and c.last_used_at and (now - c.last_used_at).total_seconds() > config.idle_timeout_seconds:
                c.state = "closed"
                closed += 1
            elif c.created_at and (now - c.created_at).total_seconds() > config.max_lifetime_seconds:
                c.state = "closed"
                closed += 1
        return closed

    def get_stats(self, installation_id: str, consumer_id: str) -> PoolStats:
        key = (installation_id, consumer_id)
        config = self._configs.get(key, PoolConfig(consumer_id=consumer_id))
        conns = self._connections.get(key, [])
        active = sum(1 for c in conns if c.state == "active")
        idle = sum(1 for c in conns if c.state == "idle")
        total = active + idle
        util = (total / config.max_connections * 100) if config.max_connections > 0 else 0
        return PoolStats(consumer_id=consumer_id, active=active, idle=idle, total=total, max_connections=config.max_connections, utilization_pct=round(util, 1))
