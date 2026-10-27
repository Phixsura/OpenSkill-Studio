"""Extension Database Connector — managed database connections for extensions."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class DbConnection:
    conn_id: str
    extension_id: str
    db_type: str  # postgres, mysql, sqlite, redis, mongodb
    host: str
    port: int
    database: str
    status: str = "connected"  # connected, disconnected, error
    pool_size: int = 5
    active_queries: int = 0
    total_queries: int = 0
    created_at: float = 0.0
    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()


class ExtDbConnectorService:
    SUPPORTED_DBS = {"postgres", "mysql", "sqlite", "redis", "mongodb"}

    def __init__(self):
        self._connections: dict[str, DbConnection] = {}
        self._counter = 0

    def connect(self, extension_id: str, db_type: str, host: str,
                port: int, database: str, pool_size: int = 5) -> DbConnection:
        if db_type not in self.SUPPORTED_DBS:
            raise ValueError(f"Unsupported database: {db_type}")
        if pool_size < 1 or pool_size > 50:
            raise ValueError("Pool size must be 1-50")
        self._counter += 1
        conn = DbConnection(conn_id=f"db-{self._counter}", extension_id=extension_id,
                            db_type=db_type, host=host, port=port, database=database,
                            pool_size=pool_size)
        self._connections[conn.conn_id] = conn
        return conn

    def query(self, conn_id: str) -> bool:
        conn = self._connections.get(conn_id)
        if not conn or conn.status != "connected": return False
        if conn.active_queries >= conn.pool_size: return False
        conn.active_queries += 1
        conn.total_queries += 1
        return True

    def release(self, conn_id: str) -> bool:
        conn = self._connections.get(conn_id)
        if not conn or conn.active_queries <= 0: return False
        conn.active_queries -= 1
        return True

    def disconnect(self, conn_id: str) -> bool:
        conn = self._connections.get(conn_id)
        if conn:
            conn.status = "disconnected"
            conn.active_queries = 0
            return True
        return False

    def get_by_extension(self, extension_id: str) -> list[DbConnection]:
        return [c for c in self._connections.values() if c.extension_id == extension_id]
