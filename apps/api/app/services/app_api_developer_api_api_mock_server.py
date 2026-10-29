"""App API Developer API Mock Server — configurable mock responses for testing."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class MockEndpoint:
    endpoint_id: str
    method: str
    path: str
    status_code: int = 200
    response_body: str = "{}"
    delay_ms: int = 0
    enabled: bool = True
    hit_count: int = 0

class AppAPIDeveloperAPIApiMockServer:
    def __init__(self) -> None:
        self._mocks: dict[tuple[str, str], MockEndpoint] = {}

    def register(self, installation_id: str, endpoint_id: str, method: str, path: str, status_code: int = 200, response_body: str = "{}", delay_ms: int = 0) -> MockEndpoint:
        if not installation_id: raise ValueError("installation_id is required")
        if not path.startswith("/"): raise ValueError("path must start with /")
        if delay_ms < 0: raise ValueError("delay_ms must be non-negative")
        key = (installation_id, endpoint_id)
        if key in self._mocks: raise ValueError(f"Mock {endpoint_id} exists")
        m = MockEndpoint(endpoint_id=endpoint_id, method=method.upper(), path=path, status_code=status_code, response_body=response_body, delay_ms=delay_ms)
        self._mocks[key] = m
        return m

    def match(self, installation_id: str, method: str, path: str) -> MockEndpoint | None:
        for (inst, _), m in self._mocks.items():
            if inst == installation_id and m.enabled and m.method == method.upper() and m.path == path:
                m.hit_count += 1
                return m
        return None

    def toggle(self, installation_id: str, endpoint_id: str, enabled: bool) -> MockEndpoint:
        key = (installation_id, endpoint_id)
        m = self._mocks.get(key)
        if m is None: raise KeyError(f"Mock {endpoint_id} not found")
        m.enabled = enabled
        return m

    def list_mocks(self, installation_id: str) -> list[MockEndpoint]:
        return [m for (inst, _), m in self._mocks.items() if inst == installation_id]

    def reset_counts(self, installation_id: str) -> None:
        for (inst, _), m in self._mocks.items():
            if inst == installation_id: m.hit_count = 0
