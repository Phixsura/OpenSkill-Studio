"""Circuit Board — service dependency health dashboard with cascade analysis.

Combines circuit breakers, health checks, and dependency graph into
a single operational dashboard view.

Implements:
- Register services with dependencies and health endpoints
- Cascade impact analysis (if X goes down, what breaks?)
- Critical path identification (services with no redundancy)
- Recovery order calculation (bottom-up from leaves)
- Operational readiness score
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import deque


@dataclass
class ServiceNode:
    name: str
    status: str = "healthy"  # healthy, degraded, down, unknown
    dependencies: list[str] = field(default_factory=list)
    redundancy: int = 1  # number of instances/replicas
    critical: bool = False  # business-critical service
    sla_target: float = 99.9


class CircuitBoardService:
    def __init__(self):
        self._services: dict[str, ServiceNode] = {}

    def register(self, name: str, dependencies: list[str] | None = None,
                 redundancy: int = 1, critical: bool = False,
                 sla_target: float = 99.9) -> ServiceNode:
        node = ServiceNode(name=name, dependencies=dependencies or [],
                           redundancy=redundancy, critical=critical,
                           sla_target=sla_target)
        self._services[name] = node
        return node

    def set_status(self, name: str, status: str) -> None:
        if name in self._services:
            self._services[name].status = status

    def cascade_impact(self, failed_service: str) -> dict:
        """What breaks if this service goes down?"""
        impacted = set()
        queue = deque([failed_service])
        visited = set()

        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)

            # Find all services that depend on current
            for name, svc in self._services.items():
                if current in svc.dependencies and name not in impacted:
                    impacted.add(name)
                    queue.append(name)

        critical_impacted = [s for s in impacted
                             if self._services.get(s, ServiceNode("")).critical]
        return {
            "failed": failed_service,
            "total_impacted": len(impacted),
            "impacted_services": sorted(impacted),
            "critical_impacted": sorted(critical_impacted),
            "blast_radius_pct": round(len(impacted) / max(1, len(self._services)) * 100, 1),
        }

    def find_critical_paths(self) -> list[str]:
        """Services that are single points of failure (no redundancy + dependents)."""
        spofs = []
        for name, svc in self._services.items():
            if svc.redundancy <= 1:
                # Check if anything depends on it
                dependents = [s for s, sv in self._services.items()
                              if name in sv.dependencies]
                if dependents:
                    spofs.append(name)
        return sorted(spofs)

    def recovery_order(self) -> list[list[str]]:
        """Calculate recovery order: start from services with no deps (leaves)."""
        remaining = set(self._services.keys())
        order = []

        while remaining:
            # Find services whose deps are all recovered (not in remaining)
            batch = []
            for name in remaining:
                deps = self._services[name].dependencies
                if all(d not in remaining for d in deps if d in self._services):
                    batch.append(name)
            if not batch:
                # Circular deps — add remaining
                order.append(sorted(remaining))
                break
            order.append(sorted(batch))
            remaining -= set(batch)

        return order

    def readiness_score(self) -> dict:
        """Operational readiness: % of services healthy, weighted by criticality."""
        if not self._services:
            return {"score": 100, "status": "unknown"}

        total_weight = 0
        healthy_weight = 0
        for svc in self._services.values():
            weight = 3 if svc.critical else 1
            total_weight += weight
            if svc.status == "healthy":
                healthy_weight += weight
            elif svc.status == "degraded":
                healthy_weight += weight * 0.5

        score = round(healthy_weight / max(1, total_weight) * 100, 1)
        status = "operational" if score >= 95 else "degraded" if score >= 70 else "outage"
        return {"score": score, "status": status,
                "healthy": sum(1 for s in self._services.values() if s.status == "healthy"),
                "total": len(self._services)}

    def get_board(self) -> list[dict]:
        """Full dashboard view."""
        return [{"name": s.name, "status": s.status,
                 "dependencies": s.dependencies,
                 "critical": s.critical, "redundancy": s.redundancy}
                for s in sorted(self._services.values(), key=lambda s: s.name)]
