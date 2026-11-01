"""Endpoint Load Balancer — weighted round-robin with health-aware routing."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class BackendTarget:
    target_id: str
    url: str
    weight: int = 1
    healthy: bool = True
    current_connections: int = 0
    total_requests: int = 0


@dataclass
class LoadBalancer:
    """Weighted round-robin load balancer with health awareness."""

    _targets: dict[str, BackendTarget] = field(default_factory=dict)
    _rr_index: int = 0
    _algorithm: str = "weighted_round_robin"  # weighted_round_robin, least_connections

    def add_target(self, target: BackendTarget) -> dict:
        if target.target_id in self._targets:
            raise ValueError(f"Target {target.target_id} already exists")
        if target.weight < 1:
            raise ValueError("Weight must be at least 1")
        self._targets[target.target_id] = target
        logger.info("target_added", target_id=target.target_id, url=target.url)
        return {"target_id": target.target_id, "total_targets": len(self._targets)}

    def remove_target(self, target_id: str) -> dict:
        if target_id not in self._targets:
            return {"removed": False}
        del self._targets[target_id]
        return {"removed": True, "remaining": len(self._targets)}

    def set_algorithm(self, algorithm: str) -> dict:
        if algorithm not in ("weighted_round_robin", "least_connections"):
            raise ValueError(f"Unknown algorithm: {algorithm}")
        self._algorithm = algorithm
        return {"algorithm": algorithm}

    def set_health(self, target_id: str, healthy: bool) -> dict:
        target = self._targets.get(target_id)
        if not target:
            raise ValueError(f"Target {target_id} not found")
        target.healthy = healthy
        logger.info("health_updated", target_id=target_id, healthy=healthy)
        return {"target_id": target_id, "healthy": healthy}

    def route(self) -> dict | None:
        healthy = [t for t in self._targets.values() if t.healthy]
        if not healthy:
            return None
        if self._algorithm == "least_connections":
            target = min(healthy, key=lambda t: t.current_connections)
        else:
            # Weighted round-robin: build expanded list
            expanded = []
            for t in healthy:
                expanded.extend([t] * t.weight)
            if not expanded:
                return None
            self._rr_index = self._rr_index % len(expanded)
            target = expanded[self._rr_index]
            self._rr_index += 1
        target.current_connections += 1
        target.total_requests += 1
        return {"target_id": target.target_id, "url": target.url,
                "connections": target.current_connections}

    def release(self, target_id: str) -> dict:
        target = self._targets.get(target_id)
        if not target:
            return {"error": "not_found"}
        target.current_connections = max(0, target.current_connections - 1)
        return {"target_id": target_id, "connections": target.current_connections}

    def get_stats(self) -> dict:
        targets = list(self._targets.values())
        healthy_count = sum(1 for t in targets if t.healthy)
        total_conns = sum(t.current_connections for t in targets)
        total_reqs = sum(t.total_requests for t in targets)
        return {
            "total_targets": len(targets),
            "healthy": healthy_count,
            "unhealthy": len(targets) - healthy_count,
            "active_connections": total_conns,
            "total_requests": total_reqs,
            "algorithm": self._algorithm,
        }

    def list_targets(self) -> list[dict]:
        return [
            {"target_id": t.target_id, "url": t.url, "weight": t.weight,
             "healthy": t.healthy, "connections": t.current_connections,
             "total_requests": t.total_requests}
            for t in self._targets.values()
        ]
