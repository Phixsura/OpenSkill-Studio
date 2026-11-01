"""Graceful shutdown coordinator — orchestrate zero-downtime shutdowns."""
from __future__ import annotations
import time


class ShutdownCoordinator:
    def __init__(self, drain_seconds: int = 30):
        self._drain = drain_seconds
        self._connections: list[dict] = []
        self._state = "running"

    def register_connection(self, conn_id: str, started_at: float) -> None:
        self._connections.append({"id": conn_id, "started_at": started_at})

    def initiate_shutdown(self) -> dict:
        self._state = "draining"
        active = len(self._connections)
        return {"state": self._state, "active_connections": active,
                "drain_seconds": self._drain, "action": "stop_accepting_new"}

    def drain_complete(self) -> dict:
        self._connections.clear()
        self._state = "stopped"
        return {"state": self._state, "remaining": 0, "ready_to_stop": True}

    def status(self) -> dict:
        return {"state": self._state, "active_connections": len(self._connections),
                "drain_seconds": self._drain}


def plan_rolling_restart(instances: list[str], batch_size: int = 1) -> list[dict]:
    batches = []
    for i in range(0, len(instances), batch_size):
        batch = instances[i:i + batch_size]
        batches.append({"batch": len(batches) + 1, "instances": batch,
                        "size": len(batch)})
    return batches
