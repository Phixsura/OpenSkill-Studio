"""API Gateway V2 — request routing, auth, rate limiting, transformation pipeline.

Orchestrates:
- Route matching via trie
- Authentication check
- Rate limit enforcement
- Request/response transformation
- Error standardization
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class GatewayRequest:
    method: str
    path: str
    headers: dict = field(default_factory=dict)
    body: str = ""
    client_id: str = ""


@dataclass
class GatewayResponse:
    status_code: int
    body: dict = field(default_factory=dict)
    headers: dict = field(default_factory=dict)
    latency_ms: float = 0.0


@dataclass
class RouteConfig:
    path_pattern: str
    upstream: str
    require_auth: bool = True
    rate_limit: int = 100  # requests per minute
    transform: dict = field(default_factory=dict)


class ApiGatewayV2Service:
    def __init__(self):
        self._routes: list[RouteConfig] = []
        self._request_counts: dict[str, list[float]] = {}
        self._auth_tokens: set[str] = set()
        self._request_log: list[dict] = []

    def register_route(self, path: str, upstream: str,
                       require_auth: bool = True, rate_limit: int = 100) -> RouteConfig:
        route = RouteConfig(path_pattern=path, upstream=upstream,
                            require_auth=require_auth, rate_limit=rate_limit)
        self._routes.append(route)
        return route

    def register_token(self, token: str) -> None:
        self._auth_tokens.add(token)

    def handle(self, request: GatewayRequest) -> GatewayResponse:
        start = time.time()

        # 1. Route matching
        route = self._match_route(request.path)
        if not route:
            return self._error(404, "ROUTE_NOT_FOUND", "No matching route", start)

        # 2. Authentication
        if route.require_auth:
            token = request.headers.get("Authorization", "").replace("Bearer ", "")
            if not token or token not in self._auth_tokens:
                return self._error(401, "UNAUTHORIZED", "Invalid or missing token", start)

        # 3. Rate limiting
        if not self._check_rate(request.client_id, route.rate_limit):
            return self._error(429, "RATE_LIMITED",
                               f"Rate limit exceeded ({route.rate_limit}/min)", start)

        # 4. Forward to upstream (simulated)
        latency = round((time.time() - start) * 1000, 2)
        response = GatewayResponse(
            status_code=200,
            body={"upstream": route.upstream, "path": request.path,
                  "method": request.method},
            headers={"X-Gateway-Latency": f"{latency}ms"},
            latency_ms=latency)

        self._log_request(request, response)
        return response

    def _match_route(self, path: str) -> RouteConfig | None:
        for route in self._routes:
            if path.startswith(route.path_pattern):
                return route
        return None

    def _check_rate(self, client_id: str, limit: int) -> bool:
        now = time.time()
        if client_id not in self._request_counts:
            self._request_counts[client_id] = []
        times = self._request_counts[client_id]
        # Clean old entries
        cutoff = now - 60
        self._request_counts[client_id] = [t for t in times if t > cutoff]
        if len(self._request_counts[client_id]) >= limit:
            return False
        self._request_counts[client_id].append(now)
        return True

    def _error(self, status: int, code: str, message: str, start: float) -> GatewayResponse:
        return GatewayResponse(
            status_code=status,
            body={"error": {"code": code, "message": message}},
            latency_ms=round((time.time() - start) * 1000, 2))

    def _log_request(self, req: GatewayRequest, resp: GatewayResponse) -> None:
        self._request_log.append({
            "method": req.method, "path": req.path,
            "status": resp.status_code, "latency_ms": resp.latency_ms})

    def get_metrics(self) -> dict:
        total = len(self._request_log)
        errors = sum(1 for r in self._request_log if r["status"] >= 400)
        avg_latency = (sum(r["latency_ms"] for r in self._request_log) / total) if total else 0
        return {"total_requests": total, "error_count": errors,
                "error_rate": round(errors / max(1, total) * 100, 1),
                "avg_latency_ms": round(avg_latency, 2)}
