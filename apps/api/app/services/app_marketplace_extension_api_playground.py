"""API Playground Executor — sandbox API execution for developer testing.

Executes API requests in a sandboxed environment with request/response
capture, execution history, variable interpolation, and response assertions.
"""
from __future__ import annotations
import json
import re
import secrets
import time
from dataclasses import dataclass, field


@dataclass
class PlaygroundRequest:
    method: str
    path: str
    headers: dict[str, str] = field(default_factory=dict)
    body: str = ""
    query_params: dict[str, str] = field(default_factory=dict)


@dataclass
class PlaygroundResponse:
    status_code: int
    headers: dict[str, str] = field(default_factory=dict)
    body: str = ""
    latency_ms: float = 0.0


@dataclass
class ExecutionRecord:
    execution_id: str
    request: PlaygroundRequest
    response: PlaygroundResponse
    assertions_passed: int = 0
    assertions_failed: int = 0
    assertion_results: list[dict] = field(default_factory=list)
    timestamp: float = 0.0


MOCK_ENDPOINTS: dict[str, dict] = {
    "GET /api/v1/extensions": {"status": 200, "body": {"data": [], "meta": {"total": 0}}},
    "GET /api/v1/extensions/{id}": {"status": 200, "body": {"data": {"id": "ext-1", "name": "Test"}}},
    "POST /api/v1/extensions": {"status": 201, "body": {"data": {"id": "ext-new"}}},
    "DELETE /api/v1/extensions/{id}": {"status": 204, "body": {}},
    "GET /api/v1/health": {"status": 200, "body": {"status": "ok"}},
}


class ApiPlaygroundService:
    """Executes sandboxed API requests with assertions."""

    def __init__(self):
        self._history: list[ExecutionRecord] = []
        self._variables: dict[str, str] = {}
        self._custom_mocks: dict[str, dict] = {}

    def set_variable(self, key: str, value: str) -> None:
        self._variables[key] = value

    def set_mock(self, method: str, path: str, status: int, body: dict) -> None:
        self._custom_mocks[f"{method} {path}"] = {"status": status, "body": body}

    def _interpolate(self, text: str) -> str:
        def replacer(match: re.Match) -> str:
            return self._variables.get(match.group(1), match.group(0))
        return re.sub(r"\{\{(\w+)\}\}", replacer, text)

    def _resolve_endpoint(self, method: str, path: str) -> dict:
        key = f"{method} {path}"
        if key in self._custom_mocks:
            return self._custom_mocks[key]
        if key in MOCK_ENDPOINTS:
            return MOCK_ENDPOINTS[key]
        # Try pattern matching
        for pattern, response in {**MOCK_ENDPOINTS, **self._custom_mocks}.items():
            pat_method, pat_path = pattern.split(" ", 1)
            if pat_method != method:
                continue
            regex = re.sub(r"\{[^}]+\}", r"[^/]+", pat_path)
            if re.fullmatch(regex, path):
                return response
        return {"status": 404, "body": {"error": {"code": "NOT_FOUND", "message": "Endpoint not found"}}}

    def execute(self, request: PlaygroundRequest,
                assertions: list[dict] | None = None) -> ExecutionRecord:
        # Interpolate variables
        path = self._interpolate(request.path)
        body = self._interpolate(request.body) if request.body else ""
        headers = {k: self._interpolate(v) for k, v in request.headers.items()}

        start = time.time()
        endpoint = self._resolve_endpoint(request.method.upper(), path)
        latency = (time.time() - start) * 1000

        response = PlaygroundResponse(
            status_code=endpoint["status"],
            body=json.dumps(endpoint["body"]),
            latency_ms=round(latency, 2),
            headers={"content-type": "application/json"},
        )

        record = ExecutionRecord(
            execution_id=f"exec_{secrets.token_urlsafe(8)}",
            request=PlaygroundRequest(
                method=request.method.upper(), path=path,
                headers=headers, body=body, query_params=request.query_params,
            ),
            response=response, timestamp=time.time(),
        )

        # Record in history before processing assertions
        self._history.append(record)

        # Run assertions
        for assertion in (assertions or []):
            result = self._check_assertion(response, assertion)
            record.assertion_results.append(result)
            if result["passed"]:
                record.assertions_passed += 1
            else:
                record.assertions_failed += 1

        return record

    def _check_assertion(self, response: PlaygroundResponse,
                         assertion: dict) -> dict:
        check = assertion.get("check", "")
        expected = assertion.get("expected")

        if check == "status":
            passed = response.status_code == expected
            return {"check": check, "passed": passed,
                    "actual": response.status_code, "expected": expected}
        elif check == "body_contains":
            passed = expected in response.body
            return {"check": check, "passed": passed, "expected": expected}
        elif check == "header_exists":
            passed = expected in response.headers
            return {"check": check, "passed": passed, "expected": expected}
        return {"check": check, "passed": False, "reason": "Unknown assertion"}

    def get_history(self, limit: int = 20) -> list[ExecutionRecord]:
        return self._history[-limit:]

    def clear_history(self) -> int:
        count = len(self._history)
        self._history.clear()
        return count
