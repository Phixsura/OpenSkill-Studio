"""Endpoint Dependency Map — track dependencies between API endpoints."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class Dependency:
    from_endpoint: str
    to_endpoint: str
    dependency_type: str = "calls"  # "calls", "reads_from", "writes_to", "triggers"
    critical: bool = False  # if True, from_endpoint cannot function without to_endpoint

@dataclass
class ImpactAnalysis:
    endpoint: str
    direct_dependents: list[str] = field(default_factory=list)
    transitive_dependents: list[str] = field(default_factory=list)
    critical_chain: bool = False

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointDependencyMap:
    def __init__(self) -> None:
        self._deps: dict[tuple[str, str, str], Dependency] = {}  # (inst, from, to)

    def add_dependency(self, installation_id: str, dep: Dependency) -> Dependency:
        if not installation_id:
            raise ValueError("installation_id is required")
        if dep.from_endpoint == dep.to_endpoint:
            raise ValueError("Self-dependency not allowed")
        if dep.dependency_type not in ("calls", "reads_from", "writes_to", "triggers"):
            raise ValueError(f"Invalid type: {dep.dependency_type}")
        key = (installation_id, dep.from_endpoint, dep.to_endpoint)
        self._deps[key] = dep
        return dep

    def remove_dependency(self, installation_id: str, from_ep: str, to_ep: str) -> None:
        key = (installation_id, from_ep, to_ep)
        if key not in self._deps:
            raise ValueError("Dependency not found")
        del self._deps[key]

    def get_dependencies(self, installation_id: str, endpoint: str) -> list[Dependency]:
        return [d for (inst, frm, _), d in self._deps.items() if inst == installation_id and frm == endpoint]

    def get_dependents(self, installation_id: str, endpoint: str) -> list[Dependency]:
        return [d for (inst, _, to), d in self._deps.items() if inst == installation_id and to == endpoint]

    def analyze_impact(self, installation_id: str, endpoint: str) -> ImpactAnalysis:
        direct = [d.from_endpoint for (inst, _, to), d in self._deps.items() if inst == installation_id and to == endpoint]
        # BFS for transitive
        visited: set[str] = set()
        queue = list(direct)
        while queue:
            ep = queue.pop(0)
            if ep in visited:
                continue
            visited.add(ep)
            upstream = [d.from_endpoint for (inst, _, to), d in self._deps.items() if inst == installation_id and to == ep]
            queue.extend(upstream)
        transitive = sorted(visited - set(direct))
        # Check if any critical path
        critical = any(d.critical for (inst, _, to), d in self._deps.items() if inst == installation_id and to == endpoint)
        return ImpactAnalysis(endpoint=endpoint, direct_dependents=sorted(direct), transitive_dependents=transitive, critical_chain=critical)

    def list_all(self, installation_id: str) -> list[Dependency]:
        return [d for (inst, _, _), d in self._deps.items() if inst == installation_id]
