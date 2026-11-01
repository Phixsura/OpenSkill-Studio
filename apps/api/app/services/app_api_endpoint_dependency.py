"""App API Endpoint Dependency — track dependencies between endpoints."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class EndpointDep:
    method: str
    path: str
    depends_on: list[str] = field(default_factory=list)  # ["GET /api/auth"]

class AppAPIEndpointDependency:
    def __init__(self) -> None:
        self._deps: dict[tuple[str, str, str], EndpointDep] = {}

    def register(self, installation_id: str, method: str, path: str, depends_on: list[str] | None = None) -> EndpointDep:
        if not installation_id: raise ValueError("installation_id is required")
        dep = EndpointDep(method=method.upper(), path=path, depends_on=depends_on or [])
        self._deps[(installation_id, method.upper(), path)] = dep
        return dep

    def dependencies_of(self, installation_id: str, method: str, path: str) -> list[str]:
        dep = self._deps.get((installation_id, method.upper(), path))
        return dep.depends_on if dep else []

    def dependents_of(self, installation_id: str, endpoint_key: str) -> list[EndpointDep]:
        return [d for (inst, _, _), d in self._deps.items() if inst == installation_id and endpoint_key in d.depends_on]

    def list_all(self, installation_id: str) -> list[EndpointDep]:
        return [d for (inst, _, _), d in self._deps.items() if inst == installation_id]
