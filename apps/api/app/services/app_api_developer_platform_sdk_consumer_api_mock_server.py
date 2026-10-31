"""API Mock Server — endpoint mocking with response templates and delays."""
from __future__ import annotations

import re
import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class MockResponse:
    status_code: int = 200
    body: dict | list | str = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    delay_ms: int = 0


@dataclass
class MockEndpoint:
    path: str
    method: str
    response: MockResponse
    match_headers: dict[str, str] = field(default_factory=dict)
    hit_count: int = 0
    enabled: bool = True


@dataclass
class MockServer:
    """In-memory mock server for API endpoint simulation."""

    _endpoints: dict[str, MockEndpoint] = field(default_factory=dict)
    _request_log: list[dict] = field(default_factory=list)

    def _key(self, method: str, path: str) -> str:
        return f"{method.upper()}:{path}"

    def register(self, path: str, method: str = "GET",
                 response: MockResponse | None = None) -> dict:
        if not path.startswith("/"):
            raise ValueError("Path must start with /")
        method = method.upper()
        if method not in ("GET", "POST", "PUT", "PATCH", "DELETE"):
            raise ValueError(f"Unsupported method: {method}")
        key = self._key(method, path)
        self._endpoints[key] = MockEndpoint(
            path=path, method=method,
            response=response or MockResponse(),
        )
        logger.info("mock_registered", method=method, path=path)
        return {"key": key, "method": method, "path": path}

    def handle_request(self, method: str, path: str,
                       headers: dict[str, str] | None = None) -> dict:
        method = method.upper()
        key = self._key(method, path)
        endpoint = self._endpoints.get(key)
        # Try pattern matching if exact match fails
        if not endpoint:
            for ep in self._endpoints.values():
                pattern = re.sub(r"\{[^}]+\}", r"[^/]+", ep.path)
                if ep.method == method and re.fullmatch(pattern, path):
                    endpoint = ep
                    break
        if not endpoint or not endpoint.enabled:
            self._request_log.append({"method": method, "path": path, "matched": False})
            return {"status_code": 404, "body": {"error": "not_found"}, "matched": False}
        # Check header matching
        if endpoint.match_headers:
            req_headers = headers or {}
            for k, v in endpoint.match_headers.items():
                if req_headers.get(k) != v:
                    return {"status_code": 412, "body": {"error": "header_mismatch"},
                            "matched": False}
        endpoint.hit_count += 1
        self._request_log.append({"method": method, "path": path, "matched": True,
                                   "status_code": endpoint.response.status_code})
        return {
            "status_code": endpoint.response.status_code,
            "body": endpoint.response.body,
            "headers": endpoint.response.headers,
            "delay_ms": endpoint.response.delay_ms,
            "matched": True,
        }

    def set_enabled(self, method: str, path: str, enabled: bool) -> dict:
        key = self._key(method, path)
        ep = self._endpoints.get(key)
        if not ep:
            return {"error": "not_found"}
        ep.enabled = enabled
        return {"key": key, "enabled": enabled}

    def get_stats(self) -> dict:
        total_hits = sum(ep.hit_count for ep in self._endpoints.values())
        return {
            "total_endpoints": len(self._endpoints),
            "enabled": sum(1 for ep in self._endpoints.values() if ep.enabled),
            "total_hits": total_hits,
            "total_requests": len(self._request_log),
            "unmatched": sum(1 for r in self._request_log if not r["matched"]),
        }

    def list_endpoints(self) -> list[dict]:
        return [
            {"method": ep.method, "path": ep.path, "status_code": ep.response.status_code,
             "hit_count": ep.hit_count, "enabled": ep.enabled}
            for ep in self._endpoints.values()
        ]

    def reset_counts(self) -> dict:
        for ep in self._endpoints.values():
            ep.hit_count = 0
        self._request_log.clear()
        return {"reset": True}
