"""Platform service discovery — register and discover services."""
from __future__ import annotations
import time


class ServiceDiscovery:
    def __init__(self, heartbeat_ttl: int = 30):
        self._services: dict[str, dict] = {}
        self._ttl = heartbeat_ttl

    def register(self, name: str, host: str, port: int, tags: list[str] | None = None) -> dict:
        self._services[name] = {"name": name, "host": host, "port": port,
                                 "tags": tags or [], "last_heartbeat": time.time(),
                                 "status": "healthy"}
        return {"registered": True, "endpoint": f"{host}:{port}"}

    def heartbeat(self, name: str) -> dict:
        if name in self._services:
            self._services[name]["last_heartbeat"] = time.time()
            return {"name": name, "alive": True}
        return {"name": name, "alive": False}

    def discover(self, tag: str = "") -> list[dict]:
        now = time.time()
        alive = []
        for s in self._services.values():
            if now - s["last_heartbeat"] > self._ttl:
                s["status"] = "stale"
                continue
            if tag and tag not in s["tags"]:
                continue
            alive.append({"name": s["name"], "endpoint": f"{s['host']}:{s['port']}",
                          "tags": s["tags"]})
        return alive

    def stats(self) -> dict:
        healthy = sum(1 for s in self._services.values() if s["status"] == "healthy")
        return {"total": len(self._services), "healthy": healthy,
                "stale": len(self._services) - healthy}
