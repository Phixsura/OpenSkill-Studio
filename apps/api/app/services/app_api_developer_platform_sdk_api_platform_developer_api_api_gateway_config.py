"""API Gateway Config — manage gateway routing and middleware configuration."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
from urllib.parse import urlparse
import structlog

log = structlog.get_logger()

@dataclass
class RouteConfig:
    route_id: str
    path_pattern: str  # e.g. "/api/v1/users/*"
    upstream: str  # target service URL
    methods: list[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"])
    middlewares: list[str] = field(default_factory=list)  # "auth", "rate_limit", "cors", "cache", "logging"
    timeout_ms: int = 30000
    enabled: bool = True

VALID_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}
VALID_MIDDLEWARES = {"auth", "rate_limit", "cors", "cache", "logging", "compression", "request_id"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiGatewayConfig:
    def __init__(self) -> None:
        self._routes: dict[tuple[str, str], RouteConfig] = {}

    def add_route(self, installation_id: str, route: RouteConfig) -> RouteConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if not route.path_pattern: raise ValueError("path_pattern is required")
        if not route.upstream: raise ValueError("upstream is required")
        parsed = urlparse(route.upstream)
        if parsed.scheme not in ("http", "https"): raise ValueError("upstream must use http or https")
        if not parsed.hostname: raise ValueError("upstream must have a hostname")
        invalid_methods = set(m.upper() for m in route.methods) - VALID_METHODS
        if invalid_methods: raise ValueError(f"Invalid methods: {invalid_methods}")
        invalid_mw = set(route.middlewares) - VALID_MIDDLEWARES
        if invalid_mw: raise ValueError(f"Invalid middlewares: {invalid_mw}")
        if route.timeout_ms < 100: raise ValueError("timeout_ms must be >= 100")
        route.methods = [m.upper() for m in route.methods]
        key = (installation_id, route.route_id)
        self._routes[key] = route
        return route

    def match_route(self, installation_id: str, method: str, path: str) -> RouteConfig | None:
        for (inst, _), r in self._routes.items():
            if inst != installation_id or not r.enabled: continue
            if method.upper() not in r.methods: continue
            pattern = "^" + re.escape(r.path_pattern).replace(r"\*", ".*") + "$"
            if re.match(pattern, path): return r
        return None

    def toggle_route(self, installation_id: str, route_id: str, enabled: bool) -> RouteConfig:
        r = self._get(installation_id, route_id)
        r.enabled = enabled
        return r

    def list_routes(self, installation_id: str) -> list[RouteConfig]:
        return [r for (inst, _), r in self._routes.items() if inst == installation_id]

    def _get(self, installation_id: str, route_id: str) -> RouteConfig:
        r = self._routes.get((installation_id, route_id))
        if r is None: raise KeyError(f"Route {route_id} not found")
        return r
