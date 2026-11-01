"""App API Gateway — route and transform API requests.

Manages API gateway routes:
- Define routes with upstream targets
- Path rewriting
- Request/response header injection
- Per-installation scoped routes
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class GatewayRoute:
    """A gateway route configuration."""

    route_id: str
    path_prefix: str
    upstream: str
    strip_prefix: bool = True
    inject_headers: dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    request_count: int = 0


class AppAPIGateway:
    """Route and transform API requests."""

    def __init__(self) -> None:
        self._routes: dict[tuple[str, str], GatewayRoute] = {}

    def add_route(
        self, installation_id: str, route_id: str, path_prefix: str,
        upstream: str, strip_prefix: bool = True,
        inject_headers: dict[str, str] | None = None,
    ) -> GatewayRoute:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not path_prefix.startswith("/"):
            raise ValueError("path_prefix must start with /")
        if not upstream:
            raise ValueError("upstream is required")

        route = GatewayRoute(
            route_id=route_id, path_prefix=path_prefix,
            upstream=upstream, strip_prefix=strip_prefix,
            inject_headers=inject_headers or {},
        )
        self._routes[(installation_id, route_id)] = route
        return route

    def resolve(self, installation_id: str, path: str) -> dict | None:
        """Resolve a request path to upstream target."""
        for (inst, _), route in self._routes.items():
            if inst != installation_id or not route.enabled:
                continue
            if path.startswith(route.path_prefix):
                route.request_count += 1
                upstream_path = path
                if route.strip_prefix:
                    upstream_path = path[len(route.path_prefix):] or "/"
                return {
                    "upstream": route.upstream,
                    "path": upstream_path,
                    "headers": dict(route.inject_headers),
                }
        return None

    def toggle(self, installation_id: str, route_id: str, enabled: bool) -> GatewayRoute:
        r = self._get(installation_id, route_id)
        r.enabled = enabled
        return r

    def list_routes(self, installation_id: str) -> list[GatewayRoute]:
        return [r for (inst, _), r in self._routes.items() if inst == installation_id]

    def _get(self, installation_id: str, route_id: str) -> GatewayRoute:
        key = (installation_id, route_id)
        r = self._routes.get(key)
        if r is None:
            raise KeyError(f"Route {route_id} not found")
        return r
