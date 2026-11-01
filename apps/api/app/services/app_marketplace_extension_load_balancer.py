"""Weighted Load Balancer — distribute requests across extension replicas.

Algorithms:
- Weighted round-robin: proportional to assigned weight
- Least connections: route to replica with fewest active connections
- Health-aware: skip unhealthy replicas, drain on health failure
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class Replica:
    replica_id: str
    url: str
    weight: int = 1  # higher = more traffic
    healthy: bool = True
    active_connections: int = 0
    total_requests: int = 0
    total_errors: int = 0
    last_health_check: float = 0.0
    draining: bool = False  # accepting no new connections


class WeightedLoadBalancerService:
    def __init__(self):
        self._pools: dict[str, list[Replica]] = {}  # service -> replicas
        self._rr_index: dict[str, int] = {}  # round-robin counter

    def add_replica(self, service: str, replica_id: str, url: str,
                    weight: int = 1) -> Replica:
        if weight < 1:
            raise ValueError("Weight must be >= 1")
        r = Replica(replica_id=replica_id, url=url, weight=weight)
        if service not in self._pools:
            self._pools[service] = []
        # No duplicate IDs
        if any(existing.replica_id == replica_id for existing in self._pools[service]):
            raise ValueError(f"Replica {replica_id} already exists")
        self._pools[service].append(r)
        return r

    def route_weighted_rr(self, service: str) -> Replica | None:
        """Weighted round-robin: build expanded list by weight, rotate index."""
        pool = self._available(service)
        if not pool:
            return None
        # Build weighted list
        expanded = []
        for r in pool:
            expanded.extend([r] * r.weight)
        if not expanded:
            return None
        idx = self._rr_index.get(service, 0)
        chosen = expanded[idx % len(expanded)]
        self._rr_index[service] = (idx + 1) % len(expanded)
        chosen.active_connections += 1
        chosen.total_requests += 1
        return chosen

    def route_least_connections(self, service: str) -> Replica | None:
        """Route to replica with fewest active connections, weighted."""
        pool = self._available(service)
        if not pool:
            return None
        # Score = active_connections / weight (lower is better)
        chosen = min(pool, key=lambda r: r.active_connections / r.weight)
        chosen.active_connections += 1
        chosen.total_requests += 1
        return chosen

    def _available(self, service: str) -> list[Replica]:
        return [r for r in self._pools.get(service, [])
                if r.healthy and not r.draining]

    def release(self, service: str, replica_id: str) -> None:
        for r in self._pools.get(service, []):
            if r.replica_id == replica_id:
                r.active_connections = max(0, r.active_connections - 1)
                return

    def report_error(self, service: str, replica_id: str,
                     health_threshold: int = 3) -> bool:
        """Report error; returns True if replica was marked unhealthy."""
        for r in self._pools.get(service, []):
            if r.replica_id == replica_id:
                r.total_errors += 1
                # Mark unhealthy after threshold consecutive-ish errors
                recent_error_rate = r.total_errors / max(1, r.total_requests)
                if r.total_errors >= health_threshold and recent_error_rate > 0.5:
                    r.healthy = False
                    return True
                return False
        return False

    def drain(self, service: str, replica_id: str) -> bool:
        """Start draining — no new connections, existing ones finish."""
        for r in self._pools.get(service, []):
            if r.replica_id == replica_id:
                r.draining = True
                return True
        return False

    def mark_healthy(self, service: str, replica_id: str) -> bool:
        for r in self._pools.get(service, []):
            if r.replica_id == replica_id:
                r.healthy = True
                r.draining = False
                r.total_errors = 0
                return True
        return False

    def get_stats(self, service: str) -> dict:
        pool = self._pools.get(service, [])
        return {
            "total_replicas": len(pool),
            "healthy": sum(1 for r in pool if r.healthy and not r.draining),
            "draining": sum(1 for r in pool if r.draining),
            "unhealthy": sum(1 for r in pool if not r.healthy),
            "total_connections": sum(r.active_connections for r in pool),
            "total_requests": sum(r.total_requests for r in pool),
        }
