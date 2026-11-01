"""Service mesh load balancer — intelligent load balancing within the mesh."""
from __future__ import annotations
import hashlib


class MeshLoadBalancer:
    def __init__(self, strategy: str = "round_robin"):
        self._strategy = strategy
        self._backends: dict[str, list[dict]] = {}
        self._idx: dict[str, int] = {}

    def register_backends(self, service: str, backends: list[dict]) -> dict:
        self._backends[service] = backends
        self._idx[service] = 0
        return {"service": service, "backends": len(backends)}

    def select(self, service: str, key: str = "") -> dict:
        backends = self._backends.get(service, [])
        healthy = [b for b in backends if b.get("healthy", True)]
        if not healthy:
            return {"selected": False, "reason": "no_healthy_backends"}
        if self._strategy == "round_robin":
            idx = self._idx.get(service, 0) % len(healthy)
            self._idx[service] = idx + 1
            selected = healthy[idx]
        elif self._strategy == "hash" and key:
            h = int(hashlib.md5(key.encode()).hexdigest(), 16)
            selected = healthy[h % len(healthy)]
        elif self._strategy == "least_conn":
            selected = min(healthy, key=lambda b: b.get("connections", 0))
        else:
            selected = healthy[0]
        return {"selected": True, "backend": selected["address"],
                "strategy": self._strategy}

    def stats(self) -> dict:
        total = sum(len(b) for b in self._backends.values())
        return {"services": len(self._backends), "total_backends": total, "strategy": self._strategy}
