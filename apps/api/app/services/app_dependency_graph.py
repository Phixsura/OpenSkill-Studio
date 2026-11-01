"""App Dependency Graph — track service dependencies.

Maps inter-service dependencies:
- Register services and their dependencies
- Detect circular dependencies
- Calculate dependency depth
- Find affected services on change
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
    version: str = ""
    depends_on: list[str] = field(default_factory=list)


class AppDependencyGraph:
    """Track and analyze service dependencies."""

    def __init__(self) -> None:
        self._nodes: dict[tuple[str, str], ServiceNode] = {}

    def register_service(
        self, installation_id: str, service_id: str, name: str,
        version: str = "", depends_on: list[str] | None = None,
    ) -> ServiceNode:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not service_id:
            raise ValueError("service_id is required")

        deps = depends_on or []
        # Validate no self-dependency
        if service_id in deps:
            raise ValueError("Service cannot depend on itself")

        node = ServiceNode(
            service_id=service_id, name=name,
            version=version, depends_on=deps,
        )
        self._nodes[(installation_id, service_id)] = node
        return node

    def get_service(self, installation_id: str, service_id: str) -> ServiceNode:
        key = (installation_id, service_id)
        n = self._nodes.get(key)
        if n is None:
            raise KeyError(f"Service {service_id} not found")
        return n

    def has_circular(self, installation_id: str) -> bool:
        """Check if the dependency graph has circular dependencies."""
        visited: set[str] = set()
        in_stack: set[str] = set()

        def _dfs(sid: str) -> bool:
            visited.add(sid)
            in_stack.add(sid)
            node = self._nodes.get((installation_id, sid))
            if node:
                for dep in node.depends_on:
                    if dep in in_stack:
                        return True
                    if dep not in visited and _dfs(dep):
                        return True
            in_stack.discard(sid)
            return False

        all_ids = [sid for (inst, sid) in self._nodes if inst == installation_id]
        for sid in all_ids:
            if sid not in visited:
                if _dfs(sid):
                    return True
        return False

    def dependency_depth(self, installation_id: str, service_id: str) -> int:
        """Calculate the maximum dependency chain depth."""
        seen: set[str] = set()

        def _depth(sid: str) -> int:
            if sid in seen:
                return 0  # break cycles
            seen.add(sid)
            node = self._nodes.get((installation_id, sid))
            if not node or not node.depends_on:
                return 0
            return 1 + max(_depth(d) for d in node.depends_on)

        return _depth(service_id)

    def affected_by(self, installation_id: str, service_id: str) -> list[str]:
        """Find all services that depend (directly or transitively) on service_id."""
        affected: set[str] = set()
        queue = [service_id]
        while queue:
            current = queue.pop(0)
            for (inst, sid), node in self._nodes.items():
                if inst == installation_id and current in node.depends_on and sid not in affected:
                    affected.add(sid)
                    queue.append(sid)
        return sorted(affected)

    def list_services(self, installation_id: str) -> list[ServiceNode]:
        return [n for (inst, _), n in self._nodes.items() if inst == installation_id]
