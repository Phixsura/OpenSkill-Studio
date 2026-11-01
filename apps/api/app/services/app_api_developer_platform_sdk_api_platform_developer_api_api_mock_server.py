"""API Mock Server — define mock responses for API testing."""
from __future__ import annotations
from dataclasses import dataclass, field
import json
import structlog

log = structlog.get_logger()

@dataclass
class MockResponse:
    mock_id: str
    method: str
    path: str
    status_code: int = 200
    body: str = "{}"
    headers: dict[str, str] = field(default_factory=dict)
    delay_ms: int = 0
    hit_count: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiMockServer:
    def __init__(self) -> None:
        self._mocks: dict[tuple[str, str, str], MockResponse] = {}

    def register_mock(self, installation_id: str, mock: MockResponse) -> MockResponse:
        if not installation_id: raise ValueError("installation_id is required")
        if not mock.method or not mock.path: raise ValueError("method and path required")
        if not 100 <= mock.status_code <= 599: raise ValueError("status_code must be 100-599")
        if mock.delay_ms < 0: raise ValueError("delay_ms must be non-negative")
        # Validate body is valid JSON if content-type is json
        ct = mock.headers.get("Content-Type", "application/json")
        if "json" in ct:
            try: json.loads(mock.body)
            except json.JSONDecodeError as e: raise ValueError(f"Invalid JSON body: {e}") from e
        key = (installation_id, mock.method.upper(), mock.path)
        self._mocks[key] = mock
        return mock

    def match(self, installation_id: str, method: str, path: str) -> MockResponse | None:
        key = (installation_id, method.upper(), path)
        mock = self._mocks.get(key)
        if mock: mock.hit_count += 1
        return mock

    def list_mocks(self, installation_id: str) -> list[MockResponse]:
        return [m for (inst, _, _), m in self._mocks.items() if inst == installation_id]

    def remove_mock(self, installation_id: str, method: str, path: str) -> bool:
        key = (installation_id, method.upper(), path)
        if key in self._mocks: del self._mocks[key]; return True
        return False

    def reset_hits(self, installation_id: str) -> int:
        count = 0
        for (inst, _, _), m in self._mocks.items():
            if inst == installation_id:
                count += m.hit_count
                m.hit_count = 0
        return count

    def total_hits(self, installation_id: str) -> int:
        return sum(m.hit_count for (inst, _, _), m in self._mocks.items() if inst == installation_id)
