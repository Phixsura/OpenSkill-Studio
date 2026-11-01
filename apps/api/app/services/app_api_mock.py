"""App API Mock — define mock responses for API endpoints.

Manages mock API responses for testing:
- Define mock responses per endpoint
- Configurable status codes and delays
- Request counting per mock
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class MockResponse:
    """A mock API response definition."""

    mock_id: str
    method: str
    path: str
    status_code: int = 200
    body: str = "{}"
    headers: dict = field(default_factory=dict)
    delay_ms: float = 0.0
    hit_count: int = 0


class AppAPIMock:
    """Define mock responses for API endpoints."""

    def __init__(self) -> None:
        self._mocks: dict[tuple[str, str], MockResponse] = {}

    def add_mock(
        self,
        installation_id: str,
        mock_id: str,
        method: str,
        path: str,
        status_code: int = 200,
        body: str = "{}",
        headers: dict | None = None,
        delay_ms: float = 0.0,
    ) -> MockResponse:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not mock_id:
            raise ValueError("mock_id is required")

        key = (installation_id, mock_id)
        if key in self._mocks:
            raise ValueError(f"Mock {mock_id} already exists")

        mock = MockResponse(
            mock_id=mock_id, method=method.upper(), path=path,
            status_code=status_code, body=body,
            headers=headers or {}, delay_ms=max(0, delay_ms),
        )
        self._mocks[key] = mock
        return mock

    def match(
        self, installation_id: str, method: str, path: str
    ) -> MockResponse | None:
        """Find a matching mock for a request."""
        for (inst, _), mock in self._mocks.items():
            if inst == installation_id and mock.method == method.upper() and mock.path == path:
                mock.hit_count += 1
                return mock
        return None

    def get_mock(self, installation_id: str, mock_id: str) -> MockResponse:
        key = (installation_id, mock_id)
        m = self._mocks.get(key)
        if m is None:
            raise KeyError(f"Mock {mock_id} not found")
        return m

    def remove_mock(self, installation_id: str, mock_id: str) -> bool:
        key = (installation_id, mock_id)
        if key in self._mocks:
            del self._mocks[key]
            return True
        return False

    def list_mocks(self, installation_id: str) -> list[MockResponse]:
        return [m for (inst, _), m in self._mocks.items() if inst == installation_id]

    def reset_counts(self, installation_id: str) -> None:
        for (inst, _), m in self._mocks.items():
            if inst == installation_id:
                m.hit_count = 0
