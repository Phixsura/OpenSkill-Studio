"""App API Webhook Test — test webhook endpoints before enabling.

Manages webhook testing:
- Send test payloads to destinations
- Verify response status and timing
- Per-installation scoped tests
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class WebhookTestResult:
    """Result of a webhook test."""

    test_id: str
    destination: str
    status_code: int | None = None
    duration_ms: float = 0.0
    success: bool = False
    error: str = ""
    tested_at: float = field(default_factory=time.time)


class AppAPIWebhookTest:
    """Test webhook endpoints before enabling."""

    def __init__(self) -> None:
        self._results: dict[str, list[WebhookTestResult]] = {}

    def record_test(
        self, installation_id: str, test_id: str, destination: str,
        status_code: int | None, duration_ms: float, error: str = "",
    ) -> WebhookTestResult:
        if not installation_id:
            raise ValueError("installation_id is required")
        success = status_code is not None and 200 <= status_code < 300
        result = WebhookTestResult(
            test_id=test_id, destination=destination,
            status_code=status_code, duration_ms=duration_ms,
            success=success, error=error,
        )
        self._results.setdefault(installation_id, []).append(result)
        return result

    def last_result(self, installation_id: str, destination: str) -> WebhookTestResult | None:
        for r in reversed(self._results.get(installation_id, [])):
            if r.destination == destination:
                return r
        return None

    def all_results(self, installation_id: str) -> list[WebhookTestResult]:
        return list(reversed(self._results.get(installation_id, [])))
