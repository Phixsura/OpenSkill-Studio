"""API Gateway — route, authenticate, and rate-limit extension API requests.

Central entry point for all extension API traffic. Handles routing
to the correct extension handler, authentication via API keys,
rate limiting, and request/response logging.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class GatewayRoute:
    path_prefix: str
    extension_id: str
    methods: list[str] = field(default_factory=lambda: ["GET"])
    requires_auth: bool = True
    rate_limit: int = 100  # requests per minute


@dataclass
class GatewayRequest:
    method: str
    path: str
    headers: dict = field(default_factory=dict)
    body: dict | None = None
    api_key: str = ""


@dataclass
class GatewayResponse:
    status_code: int
    body: dict
    headers: dict = field(default_factory=dict)
    duration_ms: float = 0.0


class APIGateway:
    """Routes and authenticates extension API requests."""

    def __init__(self):
        self._routes: list[GatewayRoute] = []
        self._valid_keys: dict[str, str] = {}  # key -> extension_id
        self._request_log: list[dict] = []
        self._rate_counters: dict[str, int] = {}

    def register_route(self, route: GatewayRoute) -> None:
        self._routes.append(route)

    def register_api_key(self, api_key: str, extension_id: str) -> None:
        self._valid_keys[api_key] = extension_id

    def _find_route(self, method: str, path: str) -> GatewayRoute | None:
        for route in self._routes:
            if path.startswith(route.path_prefix) and method in route.methods:
                return route
        return None

    def _check_rate_limit(self, key: str, limit: int) -> bool:
        count = self._rate_counters.get(key, 0)
        if count >= limit:
            return False
        self._rate_counters[key] = count + 1
        return True

    def handle_request(self, request: GatewayRequest) -> GatewayResponse:
        """Process a request through the gateway pipeline."""
        now = datetime.now(timezone.utc).isoformat()

        # 1. Route matching
        route = self._find_route(request.method, request.path)
        if not route:
            return GatewayResponse(404, {"error": "Not found"})

        # 2. Authentication + extension binding
        if route.requires_auth:
            if not request.api_key:
                return GatewayResponse(401, {"error": "API key required"})
            key_ext = self._valid_keys.get(request.api_key)
            if key_ext is None:
                return GatewayResponse(401, {"error": "Invalid API key"})
            if key_ext != route.extension_id:
                return GatewayResponse(403, {"error": "API key not authorized for this extension"})

        # 3. Rate limiting
        rate_key = f"{request.api_key}:{route.path_prefix}"
        if not self._check_rate_limit(rate_key, route.rate_limit):
            return GatewayResponse(429, {"error": "Rate limit exceeded"})

        # 4. Process request (simulated)
        response = GatewayResponse(
            200,
            {"extension_id": route.extension_id, "path": request.path,
             "method": request.method, "processed": True},
            duration_ms=5.0,
        )

        # 5. Log
        self._request_log.append({
            "method": request.method, "path": request.path,
            "status": response.status_code, "extension_id": route.extension_id,
            "timestamp": now, "duration_ms": response.duration_ms,
        })
        return response

    def get_request_log(self, extension_id: str | None = None, limit: int = 50) -> list[dict]:
        log = self._request_log
        if extension_id:
            log = [r for r in log if r.get("extension_id") == extension_id]
        return log[-limit:]

    def reset_rate_limits(self) -> None:
        self._rate_counters.clear()
