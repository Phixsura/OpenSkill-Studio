"""App API Developer API Dependency Graph — map service dependencies."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ServiceNode:
    service_id: str
    name: str
    dependencies: list[str] = field(default_factory=list)
    dependents: list[str] = field(default_factory=list)
    health: str = "healthy"  # "healthy", "degraded", "down"

class AppAPIDeveloperAPIApiDependencyGraph:
    def __init__(self) -> None:
        self._nodes: dict[tuple[str, str], ServiceNode] = {}

    def add_service(self, installation_id: str, service_id: str, name: str, dependencies: list[str] | None = None) -> ServiceNode:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, service_id)
        if key in self._nodes: raise ValueError(f"Service {service_id} exists")
        node = ServiceNode(service_id=service_id, name=name, dependencies=dependencies or [])
        self._nodes[key] = node
        # update dependents
        for dep_id in node.dependencies:
            dep_key = (installation_id, dep_id)
            dep = self._nodes.get(dep_key)
            if dep and service_id not in dep.dependents:
                dep.dependents.append(service_id)
        return node

    def set_health(self, installation_id: str, service_id: str, health: str) -> ServiceNode:
        if health not in ("healthy", "degraded", "down"): raise ValueError("invalid health")
        n = self._get(installation_id, service_id)
        n.health = health
        return n

    def impact_analysis(self, installation_id: str, service_id: str) -> list[ServiceNode]:
        """Which services are affected if this service goes down."""
        n = self._get(installation_id, service_id)
        affected: list[ServiceNode] = []
        visited: set[str] = set()
        queue = list(n.dependents)
        while queue:
            sid = queue.pop(0)
            if sid in visited: continue
            visited.add(sid)
            dep = self._nodes.get((installation_id, sid))
            if dep:
                affected.append(dep)
                queue.extend(dep.dependents)
        return affected

    def all_services(self, installation_id: str) -> list[ServiceNode]:
        return [n for (inst, _), n in self._nodes.items() if inst == installation_id]

    def _get(self, installation_id: str, service_id: str) -> ServiceNode:
        key = (installation_id, service_id)
        n = self._nodes.get(key)
        if n is None: raise KeyError(f"Service {service_id} not found")
        return n
