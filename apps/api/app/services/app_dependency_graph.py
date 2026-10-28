"""App Service Dependency Graph — track dependencies between app services.

Maps service dependencies for installed apps:
- Register services and their dependencies
- Detect circular dependencies
- Topological sort for deployment ordering
- Impact analysis (what breaks if X goes down)
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class ServiceNode:
    """A service in the dependency graph."""

    service_id: str
    name: str
    depends_on: list[str] = field(default_factory=list)


class AppDependencyGraph:
    """Track dependencies between app services."""

    def __init__(self) -> None:
        # (installation_id, service_id) → ServiceNode
        self._nodes: dict[tuple[str, str], ServiceNode] = {}

    def add_service(
        self,
        installation_id: str,
        service_id: str,
        name: str,
        depends_on: list[str] | None = None,
    ) -> ServiceNode:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not service_id:
            raise ValueError("service_id is required")

        key = (installation_id, service_id)
        if key in self._nodes:
            raise ValueError(f"Service {service_id} already exists")

        node = ServiceNode(service_id=service_id, name=name,
                           depends_on=depends_on or [])
        self._nodes[key] = node
        return node

    def get_dependencies(self, installation_id: str, service_id: str) -> list[str]:
        """Get direct dependencies of a service."""
        node = self._get(installation_id, service_id)
        return list(node.depends_on)

    def get_dependents(self, installation_id: str, service_id: str) -> list[str]:
        """Get services that depend on this service."""
        return [
            n.service_id for (inst, _), n in self._nodes.items()
            if inst == installation_id and service_id in n.depends_on
        ]

    def get_impact(self, installation_id: str, service_id: str) -> list[str]:
        """Get all services impacted if this service goes down (transitive)."""
        impacted: set[str] = set()
        queue = [service_id]
        while queue:
            current = queue.pop(0)
            for dep in self.get_dependents(installation_id, current):
                if dep not in impacted:
                    impacted.add(dep)
                    queue.append(dep)
        return sorted(impacted)

    def has_circular(self, installation_id: str) -> bool:
        """Check if the graph has circular dependencies."""
        services = [
            sid for (inst, sid) in self._nodes if inst == installation_id
        ]
        visited: set[str] = set()
        in_stack: set[str] = set()

        def dfs(sid: str) -> bool:
            visited.add(sid)
            in_stack.add(sid)
            node = self._nodes.get((installation_id, sid))
            if node:
                for dep in node.depends_on:
                    if dep in in_stack:
                        return True
                    if dep not in visited and dfs(dep):
                        return True
            in_stack.discard(sid)
            return False

        return any(dfs(s) for s in services if s not in visited)

    def topological_sort(self, installation_id: str) -> list[str]:
        """Return services in dependency order (dependencies first)."""
        if self.has_circular(installation_id):
            raise ValueError("Cannot sort: circular dependency detected")

        services = {
            sid: self._nodes[(installation_id, sid)]
            for (inst, sid) in self._nodes if inst == installation_id
        }
        result: list[str] = []
        visited: set[str] = set()

        def visit(sid: str) -> None:
            if sid in visited:
                return
            visited.add(sid)
            node = services.get(sid)
            if node:
                for dep in node.depends_on:
                    visit(dep)
            result.append(sid)

        for sid in services:
            visit(sid)
        return result

    def list_services(self, installation_id: str) -> list[ServiceNode]:
        return [n for (inst, _), n in self._nodes.items() if inst == installation_id]

    def _get(self, installation_id: str, service_id: str) -> ServiceNode:
        key = (installation_id, service_id)
        node = self._nodes.get(key)
        if node is None:
            raise KeyError(f"Service {service_id} not found")
        return node
