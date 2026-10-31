"""App API Developer API Gateway Config — manage gateway routing and middleware."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class GatewayRoute:
    route_id: str
    path_pattern: str
    upstream: str
    methods: list[str] = field(default_factory=lambda: ["GET"])
    rate_limit: int | None = None  # requests per minute
    auth_required: bool = True
    timeout_ms: int = 30000
    enabled: bool = True

class AppAPIDeveloperAPIApiGatewayConfig:
    def __init__(self) -> None:
        self._routes: dict[tuple[str, str], GatewayRoute] = {}

    def add_route(self, installation_id: str, route_id: str, path_pattern: str, upstream: str, methods: list[str] | None = None, rate_limit: int | None = None, auth_required: bool = True, timeout_ms: int = 30000) -> GatewayRoute:
        if not installation_id: raise ValueError("installation_id is required")
        if not path_pattern.startswith("/"): raise ValueError("path_pattern must start with /")
        key = (installation_id, route_id)
        if key in self._routes: raise ValueError(f"Route {route_id} exists")
        r = GatewayRoute(route_id=route_id, path_pattern=path_pattern, upstream=upstream, methods=methods or ["GET"], rate_limit=rate_limit, auth_required=auth_required, timeout_ms=timeout_ms)
        self._routes[key] = r
        return r

    def toggle(self, installation_id: str, route_id: str, enabled: bool) -> GatewayRoute:
        r = self._get(installation_id, route_id)
        r.enabled = enabled
        return r

    def match(self, installation_id: str, path: str, method: str) -> GatewayRoute | None:
        for (inst, _), r in self._routes.items():
            if inst == installation_id and r.enabled and path.startswith(r.path_pattern.rstrip("*")) and method.upper() in r.methods:
                return r
        return None

    def list_routes(self, installation_id: str) -> list[GatewayRoute]:
        return [r for (inst, _), r in self._routes.items() if inst == installation_id]

    def _get(self, installation_id: str, route_id: str) -> GatewayRoute:
        key = (installation_id, route_id)
        r = self._routes.get(key)
        if r is None: raise KeyError(f"Route {route_id} not found")
        return r
