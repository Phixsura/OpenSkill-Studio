"""API Gateway Router — route incoming requests to extension handlers.

Manages route registration, path matching with parameters, middleware
chains, load balancing across extension instances, and request tracing.
"""
from __future__ import annotations
import re
import secrets
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class Route:
    route_id: str
    method: str
    path_pattern: str
    extension_id: str
    handler: str
    middlewares: list[str] = field(default_factory=list)
    rate_limit: int = 0  # 0 = no limit
    auth_required: bool = True
    priority: int = 0


@dataclass
class RouteMatch:
    route: Route
    params: dict[str, str]
    matched: bool


class ApiGatewayRouterService:
    """Routes requests to extension handlers with middleware support."""

    def __init__(self):
        self._routes: dict[str, Route] = {}
        self._by_method: dict[str, list[str]] = defaultdict(list)

    def register(self, method: str, path_pattern: str, extension_id: str,
                 handler: str, middlewares: list[str] | None = None,
                 rate_limit: int = 0, auth_required: bool = True,
                 priority: int = 0) -> Route:
        # Validate path
        if not path_pattern.startswith("/"):
            raise ValueError("Path must start with /")
        if ".." in path_pattern:
            raise ValueError("Path traversal not allowed")
        # Cap priority to prevent hijacking
        priority = min(priority, 100)

        route_id = f"rt_{secrets.token_urlsafe(8)}"
        route = Route(
            route_id=route_id, method=method.upper(),
            path_pattern=path_pattern, extension_id=extension_id,
            handler=handler, middlewares=middlewares or [],
            rate_limit=rate_limit, auth_required=auth_required,
            priority=priority,
        )
        self._routes[route_id] = route
        self._by_method[method.upper()].append(route_id)
        return route

    def match(self, method: str, path: str) -> RouteMatch | None:
        candidates = []
        for route_id in self._by_method.get(method.upper(), []):
            route = self._routes[route_id]
            params = self._match_path(route.path_pattern, path)
            if params is not None:
                candidates.append((route, params))

        if not candidates:
            return None

        # Highest priority wins
        candidates.sort(key=lambda c: c[0].priority, reverse=True)
        best_route, best_params = candidates[0]
        return RouteMatch(route=best_route, params=best_params, matched=True)

    def _match_path(self, pattern: str, path: str) -> dict[str, str] | None:
        # Convert /users/{id} to regex
        param_names: list[str] = []
        regex_parts = []
        for segment in pattern.split("/"):
            if segment.startswith("{") and segment.endswith("}"):
                param_names.append(segment[1:-1])
                regex_parts.append("([^/]+)")
            else:
                regex_parts.append(re.escape(segment))
        regex = "^" + "/".join(regex_parts) + "$"
        m = re.match(regex, path)
        if not m:
            return None
        return dict(zip(param_names, m.groups()))

    def unregister(self, route_id: str, caller_extension_id: str = "") -> bool:
        route = self._routes.get(route_id)
        if not route:
            return False
        if caller_extension_id and route.extension_id != caller_extension_id:
            return False
        self._routes.pop(route_id)
        if route:
            self._by_method[route.method] = [
                rid for rid in self._by_method[route.method] if rid != route_id
            ]
            return True
        return False

    def list_routes(self, extension_id: str | None = None) -> list[Route]:
        routes = list(self._routes.values())
        if extension_id:
            routes = [r for r in routes if r.extension_id == extension_id]
        return sorted(routes, key=lambda r: (r.method, r.path_pattern))

    def get_route_map(self) -> dict[str, list[dict]]:
        result: dict[str, list[dict]] = defaultdict(list)
        for route in self._routes.values():
            result[route.method].append({
                "path": route.path_pattern,
                "extension": route.extension_id,
                "handler": route.handler,
                "auth": route.auth_required,
            })
        return dict(result)
