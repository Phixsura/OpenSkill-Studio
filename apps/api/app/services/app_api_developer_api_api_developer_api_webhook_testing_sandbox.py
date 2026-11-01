"""App API Developer Webhook Testing Sandbox — test webhook configurations safely."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class TestDelivery:
    test_id: str
    destination: str
    event_type: str
    payload: str
    status_code: int = 0
    response_body: str = ""
    duration_ms: float = 0.0
    success: bool = False
    tested_at: float = field(default_factory=time.time)

class AppAPIDeveloperAPIApiDeveloperApiWebhookTestingSandbox:
    def __init__(self) -> None:
        self._tests: dict[str, list[TestDelivery]] = {}

    def send_test(self, installation_id: str, test_id: str, destination: str, event_type: str, payload: str, status_code: int, response_body: str = "", duration_ms: float = 0.0) -> TestDelivery:
        if not installation_id: raise ValueError("installation_id is required")
        if not destination.startswith("https://"): raise ValueError("destination must use HTTPS")
        success = 200 <= status_code < 300
        t = TestDelivery(test_id=test_id, destination=destination, event_type=event_type, payload=payload[:5000], status_code=status_code, response_body=response_body[:1000], duration_ms=duration_ms, success=success)
        self._tests.setdefault(installation_id, []).append(t)
        return t

    def history(self, installation_id: str, limit: int = 20) -> list[TestDelivery]:
        return list(reversed(self._tests.get(installation_id, [])[-limit:]))

    def success_rate(self, installation_id: str) -> float:
        tests = self._tests.get(installation_id, [])
        if not tests: return 0.0
        return round(sum(1 for t in tests if t.success) / len(tests) * 100, 1)

    def by_destination(self, installation_id: str, destination: str) -> list[TestDelivery]:
        return [t for t in self._tests.get(installation_id, []) if t.destination == destination]
