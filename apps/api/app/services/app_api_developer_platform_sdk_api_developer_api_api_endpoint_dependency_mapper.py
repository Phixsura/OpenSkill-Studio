"""App API Developer Endpoint Dependency Mapper — map dependencies between endpoints."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class EndpointDependency:
    endpoint: str
    depends_on: list[str] = field(default_factory=list)
    depended_by: list[str] = field(default_factory=list)

    @property
    def dependency_count(self) -> int:
        return len(self.depends_on)

    @property
    def dependent_count(self) -> int:
        return len(self.depended_by)

    @property
    def is_critical(self) -> bool:
        return self.dependent_count >= 5

class AppAPIDeveloperPlatformSDKApiDeveloperApiApiEndpointDependencyMapper:
    def __init__(self) -> None:
        self._deps: dict[tuple[str, str], EndpointDependency] = {}

    def add_dependency(self, installation_id: str, endpoint: str, depends_on: str) -> EndpointDependency:
        if not installation_id: raise ValueError("installation_id is required")
        if endpoint == depends_on: raise ValueError("endpoint cannot depend on itself")
        # Update the source endpoint
        key = (installation_id, endpoint)
        if key not in self._deps:
            self._deps[key] = EndpointDependency(endpoint=endpoint)
        e = self._deps[key]
        if depends_on not in e.depends_on:
            e.depends_on.append(depends_on)
        # Update the target's depended_by
        dep_key = (installation_id, depends_on)
        if dep_key not in self._deps:
            self._deps[dep_key] = EndpointDependency(endpoint=depends_on)
        d = self._deps[dep_key]
        if endpoint not in d.depended_by:
            d.depended_by.append(endpoint)
        return e

    def impact_of(self, installation_id: str, endpoint: str) -> list[str]:
        key = (installation_id, endpoint)
        e = self._deps.get(key)
        return list(e.depended_by) if e else []

    def critical_endpoints(self, installation_id: str) -> list[EndpointDependency]:
        return [e for (inst, _), e in self._deps.items() if inst == installation_id and e.is_critical]

    def all_endpoints(self, installation_id: str) -> list[EndpointDependency]:
        return [e for (inst, _), e in self._deps.items() if inst == installation_id]
