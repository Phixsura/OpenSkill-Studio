"""App API Developer Versioned Endpoint Router — route requests to versioned handlers."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class VersionedRoute:
    endpoint: str
    versions: dict[str, str] = field(default_factory=dict)  # version -> handler_id
    default_version: str = ""
    request_counts: dict[str, int] = field(default_factory=dict)

class AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiVersionedEndpointRouter:
    def __init__(self) -> None:
        self._routes: dict[tuple[str, str], VersionedRoute] = {}

    def register(self, installation_id: str, endpoint: str, version: str, handler_id: str, default: bool = False) -> VersionedRoute:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, endpoint)
        if key not in self._routes:
            self._routes[key] = VersionedRoute(endpoint=endpoint)
        r = self._routes[key]
        r.versions[version] = handler_id
        r.request_counts.setdefault(version, 0)
        if default or not r.default_version: r.default_version = version
        return r

    def route(self, installation_id: str, endpoint: str, version: str | None = None) -> str:
        key = (installation_id, endpoint)
        r = self._routes.get(key)
        if r is None: raise KeyError(f"No route for {endpoint}")
        v = version or r.default_version
        handler = r.versions.get(v)
        if handler is None: raise KeyError(f"Version {v} not found for {endpoint}")
        r.request_counts[v] = r.request_counts.get(v, 0) + 1
        return handler

    def version_traffic(self, installation_id: str, endpoint: str) -> dict[str, int]:
        key = (installation_id, endpoint)
        r = self._routes.get(key)
        return dict(r.request_counts) if r else {}

    def all_routes(self, installation_id: str) -> list[VersionedRoute]:
        return [r for (inst, _), r in self._routes.items() if inst == installation_id]
