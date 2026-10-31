"""Consumer API Gateway Config — gateway routing with middleware chain."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class Middleware:
    name: str
    kind: str  # auth, rate_limit, cors, transform, logging, cache
    enabled: bool = True
    config: dict = field(default_factory=dict)
    order: int = 0


@dataclass
class Route:
    route_id: str
    path_pattern: str
    target_url: str
    methods: list[str] = field(default_factory=lambda: ["GET"])
    middlewares: list[Middleware] = field(default_factory=list)
    enabled: bool = True
    timeout_ms: int = 30000


@dataclass
class GatewayConfig:
    """Manage API gateway routing with middleware chains."""

    _routes: dict[str, Route] = field(default_factory=dict)
    _global_middlewares: list[Middleware] = field(default_factory=list)

    def add_global_middleware(self, middleware: Middleware) -> dict:
        self._global_middlewares.append(middleware)
        self._global_middlewares.sort(key=lambda m: m.order)
        logger.info("global_middleware_added", name=middleware.name)
        return {"name": middleware.name, "total": len(self._global_middlewares)}

    def add_route(self, route: Route) -> dict:
        if route.route_id in self._routes:
            raise ValueError(f"Route {route.route_id} already exists")
        if not route.path_pattern.startswith("/"):
            raise ValueError("Path pattern must start with /")
        route.middlewares.sort(key=lambda m: m.order)
        self._routes[route.route_id] = route
        logger.info("route_added", route_id=route.route_id, path=route.path_pattern)
        return {"route_id": route.route_id, "path": route.path_pattern}

    def remove_route(self, route_id: str) -> dict:
        if route_id in self._routes:
            del self._routes[route_id]
            return {"removed": True}
        return {"removed": False}

    def toggle_route(self, route_id: str, enabled: bool) -> dict:
        route = self._routes.get(route_id)
        if not route:
            raise ValueError(f"Route {route_id} not found")
        route.enabled = enabled
        return {"route_id": route_id, "enabled": enabled}

    def resolve(self, path: str, method: str = "GET") -> dict | None:
        for route in self._routes.values():
            if not route.enabled:
                continue
            if method.upper() not in [m.upper() for m in route.methods]:
                continue
            # Simple prefix match
            pattern = route.path_pattern.rstrip("*")
            if path == route.path_pattern or path.startswith(pattern):
                chain = [m for m in self._global_middlewares if m.enabled]
                chain += [m for m in route.middlewares if m.enabled]
                chain.sort(key=lambda m: m.order)
                return {
                    "route_id": route.route_id,
                    "target_url": route.target_url,
                    "timeout_ms": route.timeout_ms,
                    "middleware_chain": [m.name for m in chain],
                }
        return None

    def get_route(self, route_id: str) -> dict | None:
        route = self._routes.get(route_id)
        if not route:
            return None
        return {
            "route_id": route.route_id,
            "path": route.path_pattern,
            "target": route.target_url,
            "methods": route.methods,
            "enabled": route.enabled,
            "middleware_count": len(route.middlewares),
            "timeout_ms": route.timeout_ms,
        }

    def list_routes(self) -> list[dict]:
        return [self.get_route(r.route_id) for r in self._routes.values()]

    def get_stats(self) -> dict:
        routes = list(self._routes.values())
        return {
            "total_routes": len(routes),
            "enabled": sum(1 for r in routes if r.enabled),
            "disabled": sum(1 for r in routes if not r.enabled),
            "global_middlewares": len(self._global_middlewares),
        }
