"""API Mock Server — configurable mock API server for extension testing.

Create mock endpoints with custom responses, latency simulation,
request matching, response templating, and request recording.
"""
from __future__ import annotations
import json
import re
import secrets
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class MockEndpoint:
    endpoint_id: str
    method: str
    path_pattern: str
    status_code: int = 200
    response_body: dict | str = ""
    response_headers: dict[str, str] = field(default_factory=dict)
    latency_ms: int = 0
    match_headers: dict[str, str] = field(default_factory=dict)
    match_body: dict | None = None
    call_count: int = 0
    enabled: bool = True


@dataclass
class RecordedRequest:
    method: str
    path: str
    headers: dict[str, str]
    body: str
    matched_endpoint: str
    timestamp: float = 0.0


class ApiMockServerService:
    """Manages mock API endpoints for extension testing."""

    def __init__(self):
        self._endpoints: dict[str, MockEndpoint] = {}
        self._requests: list[RecordedRequest] = []

    def add_endpoint(self, method: str, path_pattern: str,
                     status_code: int = 200,
                     response_body: dict | str = "",
                     latency_ms: int = 0,
                     match_headers: dict[str, str] | None = None,
                     match_body: dict | None = None) -> MockEndpoint:
        endpoint_id = f"mock_{secrets.token_urlsafe(8)}"
        ep = MockEndpoint(
            endpoint_id=endpoint_id, method=method.upper(),
            path_pattern=path_pattern, status_code=status_code,
            response_body=response_body, latency_ms=min(latency_ms, 10000),
            match_headers=match_headers or {},
            match_body=match_body,
        )
        self._endpoints[endpoint_id] = ep
        return ep

    def handle_request(self, method: str, path: str,
                       headers: dict[str, str] | None = None,
                       body: str = "") -> dict:
        headers = headers or {}
        for ep in self._endpoints.values():
            if not ep.enabled:
                continue
            if ep.method != method.upper():
                continue
            # Path matching
            pattern = ep.path_pattern.replace("{", "(?P<").replace("}", ">[^/]+)")
            if not re.fullmatch(pattern, path):
                continue
            # Header matching
            if ep.match_headers:
                if not all(headers.get(k) == v for k, v in ep.match_headers.items()):
                    continue
            # Body matching
            if ep.match_body and body:
                try:
                    parsed = json.loads(body)
                    if not all(parsed.get(k) == v for k, v in ep.match_body.items()):
                        continue
                except json.JSONDecodeError:
                    continue

            ep.call_count += 1
            self._requests.append(RecordedRequest(
                method=method, path=path, headers=headers,
                body=body, matched_endpoint=ep.endpoint_id,
            ))

            resp_body = ep.response_body
            if isinstance(resp_body, dict):
                resp_body = json.dumps(resp_body)

            return {
                "status_code": ep.status_code,
                "body": resp_body,
                "headers": {"content-type": "application/json", **ep.response_headers},
                "latency_ms": ep.latency_ms,
                "endpoint_id": ep.endpoint_id,
            }

        return {"status_code": 404, "body": '{"error":"No matching mock"}',
                "headers": {"content-type": "application/json"}, "latency_ms": 0}

    def get_requests(self, endpoint_id: str | None = None) -> list[RecordedRequest]:
        if endpoint_id:
            return [r for r in self._requests if r.matched_endpoint == endpoint_id]
        return list(self._requests)

    def reset(self) -> int:
        count = len(self._requests)
        self._requests.clear()
        for ep in self._endpoints.values():
            ep.call_count = 0
        return count

    def remove_endpoint(self, endpoint_id: str) -> bool:
        return self._endpoints.pop(endpoint_id, None) is not None

    def list_endpoints(self) -> list[MockEndpoint]:
        return list(self._endpoints.values())
