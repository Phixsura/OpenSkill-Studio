"""API Endpoint Dependency Graph — track inter-endpoint call dependencies."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class EndpointNode:
    endpoint_id: str
    method: str
    path: str
    calls: list[str] = field(default_factory=list)  # endpoint_ids this calls

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiEndpointDependencyGraph:
    def __init__(self) -> None:
        self._nodes: dict[tuple[str, str], EndpointNode] = {}

    def add_endpoint(self, installation_id: str, endpoint_id: str, method: str, path: str) -> EndpointNode:
        if not installation_id: raise ValueError("installation_id is required")
        node = EndpointNode(endpoint_id=endpoint_id, method=method.upper(), path=path)
        self._nodes[(installation_id, endpoint_id)] = node
        return node

    def add_dependency(self, installation_id: str, from_id: str, to_id: str) -> None:
        src = self._nodes.get((installation_id, from_id))
        if src is None: raise KeyError(f"Endpoint {from_id} not found")
        if (installation_id, to_id) not in self._nodes: raise KeyError(f"Endpoint {to_id} not found")
        if to_id == from_id: raise ValueError("Self-dependency not allowed")
        if to_id not in src.calls: src.calls.append(to_id)

    def get_dependents(self, installation_id: str, endpoint_id: str) -> list[str]:
        """Which endpoints call this one."""
        return [n.endpoint_id for (inst, _), n in self._nodes.items()
                if inst == installation_id and endpoint_id in n.calls]

    def get_dependencies(self, installation_id: str, endpoint_id: str) -> list[str]:
        node = self._nodes.get((installation_id, endpoint_id))
        return list(node.calls) if node else []

    def detect_cycles(self, installation_id: str) -> list[list[str]]:
        nodes = {eid: n for (inst, eid), n in self._nodes.items() if inst == installation_id}
        visited: set[str] = set()
        cycles: list[list[str]] = []
        def dfs(eid: str, path: list[str]) -> None:
            if eid in path:
                cycle_start = path.index(eid)
                cycles.append(path[cycle_start:] + [eid])
                return
            if eid in visited: return
            visited.add(eid)
            for dep in nodes.get(eid, EndpointNode("", "", "")).calls:
                dfs(dep, path + [eid])
        for eid in nodes: dfs(eid, [])
        return cycles

    def impact_analysis(self, installation_id: str, endpoint_id: str) -> set[str]:
        """All endpoints transitively affected if this one changes."""
        affected: set[str] = set()
        queue = [endpoint_id]
        while queue:
            current = queue.pop(0)
            for dep in self.get_dependents(installation_id, current):
                if dep not in affected:
                    affected.add(dep)
                    queue.append(dep)
        return affected
