"""Extension API Sandbox — isolated API testing environment for developers."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import json


@dataclass
class SandboxRequest:
    request_id: str
    method: str
    path: str
    headers: dict = field(default_factory=dict)
    body: str = ""
    response_code: int = 0
    response_body: str = ""
    latency_ms: float = 0.0
    timestamp: float = 0.0
    def __post_init__(self):
        if not self.timestamp: self.timestamp = time.time()


class ExtApiSandboxService:
    VALID_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}

    def __init__(self):
        self._history: dict[str, list[SandboxRequest]] = {}  # dev_id -> requests
        self._mocks: dict[str, dict] = {}  # path -> {code, body}
        self._counter = 0

    def add_mock(self, path: str, method: str, response_code: int = 200,
                 response_body: str = "{}") -> None:
        self._mocks[f"{method}:{path}"] = {"code": response_code, "body": response_body}

    def execute(self, developer_id: str, method: str, path: str,
                headers: dict | None = None, body: str = "") -> SandboxRequest:
        if method not in self.VALID_METHODS:
            raise ValueError(f"Invalid method: {method}")
        self._counter += 1
        mock_key = f"{method}:{path}"
        mock = self._mocks.get(mock_key, {"code": 200, "body": "{}"})
        req = SandboxRequest(
            request_id=f"req-{self._counter}", method=method, path=path,
            headers=headers or {}, body=body,
            response_code=mock["code"], response_body=mock["body"],
            latency_ms=round(time.time() % 1 * 10, 1))
        if developer_id not in self._history:
            self._history[developer_id] = []
        self._history[developer_id].append(req)
        return req

    def get_history(self, developer_id: str, limit: int = 50) -> list[SandboxRequest]:
        return list(reversed(self._history.get(developer_id, [])))[:limit]

    def clear_history(self, developer_id: str) -> None:
        self._history.pop(developer_id, None)
