"""Consumer API Mock Server — define mock responses for API endpoints."""
from __future__ import annotations
from dataclasses import dataclass, field
import json
import re
import structlog

log = structlog.get_logger()

@dataclass
class MockRoute:
    route_id: str
    method: str
    path_pattern: str
    response_status: int = 200
    response_body: str = "{}"
    response_headers: dict[str, str] = field(default_factory=dict)
    delay_ms: int = 0
    enabled: bool = True

@dataclass
class MockResponse:
    matched: bool
    route_id: str | None = None
    status: int = 404
    body: str = '{"error":"not found"}'
    headers: dict[str, str] = field(default_factory=dict)
    delay_ms: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiMockServer:
    def __init__(self) -> None:
        self._routes: dict[tuple[str, str, str], MockRoute] = {}  # (inst, consumer, route_id)
        self._call_counts: dict[tuple[str, str, str], int] = {}

    def add_route(self, installation_id: str, consumer_id: str, route: MockRoute) -> MockRoute:
        if not installation_id:
            raise ValueError("installation_id is required")
        if route.method.upper() not in ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"):
            raise ValueError(f"Invalid method: {route.method}")
        if route.response_status < 100 or route.response_status > 599:
            raise ValueError("Invalid status code")
        key = (installation_id, consumer_id, route.route_id)
        self._routes[key] = route
        return route

    def remove_route(self, installation_id: str, consumer_id: str, route_id: str) -> None:
        key = (installation_id, consumer_id, route_id)
        if key not in self._routes:
            raise ValueError("Route not found")
        del self._routes[key]

    def match(self, installation_id: str, consumer_id: str, method: str, path: str) -> MockResponse:
        for (inst, cid, _), route in self._routes.items():
            if inst != installation_id or cid != consumer_id or not route.enabled:
                continue
            if route.method.upper() != method.upper():
                continue
            regex = "^" + route.path_pattern.replace("*", ".*") + "$"
            if re.match(regex, path):
                count_key = (installation_id, consumer_id, route.route_id)
                self._call_counts[count_key] = self._call_counts.get(count_key, 0) + 1
                return MockResponse(matched=True, route_id=route.route_id, status=route.response_status, body=route.response_body, headers=route.response_headers, delay_ms=route.delay_ms)
        return MockResponse(matched=False)

    def get_call_count(self, installation_id: str, consumer_id: str, route_id: str) -> int:
        return self._call_counts.get((installation_id, consumer_id, route_id), 0)

    def list_routes(self, installation_id: str, consumer_id: str) -> list[MockRoute]:
        return [r for (inst, cid, _), r in self._routes.items() if inst == installation_id and cid == consumer_id]
