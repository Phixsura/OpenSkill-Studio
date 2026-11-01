"""App Service Mesh — manage service-to-service communication policies.

Manages service mesh policies for installed apps:
- Define allowed communication paths between services
- Timeout and retry policies per route
- Track request counts per route
- Per-installation scoped mesh
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class MeshRoute:
    """A service-to-service communication route."""

    source: str
    destination: str
    allowed: bool = True
    timeout_ms: int = 5000
    max_retries: int = 3
    request_count: int = 0


class AppServiceMesh:
    """Manage service-to-service communication policies."""

    def __init__(self) -> None:
        # (installation_id, source, destination) → MeshRoute
        self._routes: dict[tuple[str, str, str], MeshRoute] = {}

    def add_route(
        self,
        installation_id: str,
        source: str,
        destination: str,
        timeout_ms: int = 5000,
        max_retries: int = 3,
    ) -> MeshRoute:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not source or not destination:
            raise ValueError("source and destination are required")
        if source == destination:
            raise ValueError("source and destination must differ")

        key = (installation_id, source, destination)
        if key in self._routes:
            raise ValueError(f"Route {source} → {destination} already exists")

        route = MeshRoute(
            source=source, destination=destination,
            timeout_ms=max(100, timeout_ms), max_retries=max(0, max_retries),
        )
        self._routes[key] = route
        return route

    def block_route(self, installation_id: str, source: str, destination: str) -> MeshRoute:
        route = self._get(installation_id, source, destination)
        route.allowed = False
        return route

    def allow_route(self, installation_id: str, source: str, destination: str) -> MeshRoute:
        route = self._get(installation_id, source, destination)
        route.allowed = True
        return route

    def can_communicate(self, installation_id: str, source: str, destination: str) -> bool:
        """Check if a route is allowed. No route = denied by default."""
        key = (installation_id, source, destination)
        route = self._routes.get(key)
        return route.allowed if route else False

    def record_request(self, installation_id: str, source: str, destination: str) -> int:
        """Record a request on a route. Returns new count."""
        route = self._get(installation_id, source, destination)
        if not route.allowed:
            raise ValueError(f"Route {source} → {destination} is blocked")
        route.request_count += 1
        return route.request_count

    def get_routes_from(self, installation_id: str, source: str) -> list[MeshRoute]:
        return [r for (inst, src, _), r in self._routes.items()
                if inst == installation_id and src == source]

    def get_routes_to(self, installation_id: str, destination: str) -> list[MeshRoute]:
        return [r for (inst, _, dst), r in self._routes.items()
                if inst == installation_id and dst == destination]

    def list_routes(self, installation_id: str) -> list[MeshRoute]:
        return [r for (inst, _, _), r in self._routes.items() if inst == installation_id]

    def _get(self, installation_id: str, source: str, destination: str) -> MeshRoute:
        key = (installation_id, source, destination)
        route = self._routes.get(key)
        if route is None:
            raise KeyError(f"Route {source} → {destination} not found")
        return route
