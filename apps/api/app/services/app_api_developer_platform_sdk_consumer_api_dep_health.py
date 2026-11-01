"""Endpoint Dependency Health — dependency health monitoring with cascade impact."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class Dependency:
    dep_id: str
    name: str
    dep_type: str  # database, cache, queue, api, storage
    healthy: bool = True
    latency_ms: float = 0.0
    error_rate: float = 0.0
    dependents: list[str] = field(default_factory=list)  # endpoint IDs


@dataclass
class DependencyHealthMonitor:
    """Monitor dependency health and analyze cascade impact."""

    _deps: dict[str, Dependency] = field(default_factory=dict)

    def register(self, dep: Dependency) -> dict:
        if dep.dep_id in self._deps:
            raise ValueError(f"Dependency {dep.dep_id} already registered")
        self._deps[dep.dep_id] = dep
        logger.info("dependency_registered", dep_id=dep.dep_id, type=dep.dep_type)
        return {"dep_id": dep.dep_id, "name": dep.name, "type": dep.dep_type}

    def update_health(self, dep_id: str, healthy: bool, latency_ms: float = 0.0,
                      error_rate: float = 0.0) -> dict:
        dep = self._deps.get(dep_id)
        if not dep:
            raise ValueError(f"Dependency {dep_id} not found")
        old_healthy = dep.healthy
        dep.healthy = healthy
        dep.latency_ms = latency_ms
        dep.error_rate = error_rate
        changed = old_healthy != healthy
        if changed and not healthy:
            logger.warning("dependency_unhealthy", dep_id=dep_id)
        return {"dep_id": dep_id, "healthy": healthy, "changed": changed}

    def add_dependent(self, dep_id: str, endpoint_id: str) -> dict:
        dep = self._deps.get(dep_id)
        if not dep:
            raise ValueError(f"Dependency {dep_id} not found")
        if endpoint_id not in dep.dependents:
            dep.dependents.append(endpoint_id)
        return {"dep_id": dep_id, "dependents": len(dep.dependents)}

    def get_cascade_impact(self, dep_id: str) -> dict:
        dep = self._deps.get(dep_id)
        if not dep:
            return {"error": "not_found"}
        affected = list(dep.dependents)
        # Check transitive: endpoints depending on other unhealthy deps
        severity = "none"
        if not dep.healthy:
            if len(affected) > 10:
                severity = "critical"
            elif len(affected) > 3:
                severity = "high"
            elif len(affected) > 0:
                severity = "medium"
        return {
            "dep_id": dep_id,
            "name": dep.name,
            "healthy": dep.healthy,
            "affected_endpoints": affected,
            "affected_count": len(affected),
            "severity": severity,
        }

    def get_health_matrix(self) -> list[dict]:
        return [
            {"dep_id": d.dep_id, "name": d.name, "type": d.dep_type,
             "healthy": d.healthy, "latency_ms": round(d.latency_ms, 2),
             "error_rate": round(d.error_rate, 4),
             "dependent_count": len(d.dependents)}
            for d in sorted(self._deps.values(), key=lambda x: x.name)
        ]

    def get_unhealthy(self) -> list[dict]:
        return [
            self.get_cascade_impact(d.dep_id)
            for d in self._deps.values() if not d.healthy
        ]

    def get_endpoint_deps(self, endpoint_id: str) -> list[dict]:
        return [
            {"dep_id": d.dep_id, "name": d.name, "healthy": d.healthy,
             "type": d.dep_type}
            for d in self._deps.values() if endpoint_id in d.dependents
        ]

    def get_stats(self) -> dict:
        deps = list(self._deps.values())
        return {
            "total": len(deps),
            "healthy": sum(1 for d in deps if d.healthy),
            "unhealthy": sum(1 for d in deps if not d.healthy),
            "total_dependents": sum(len(d.dependents) for d in deps),
        }
