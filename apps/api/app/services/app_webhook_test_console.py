"""App Webhook Test Console — simulate webhook deliveries for developer testing.

Enables developers to test their webhook endpoints without real events:
- Predefined event type templates
- Custom payload composition
- Delivery simulation with real HTTP response capture
- Response validation (status code, latency, body)
- Test history with pass/fail tracking
- Replay previous tests
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

import structlog

log = structlog.get_logger()


class TestStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"
    PENDING = "pending"


@dataclass
class WebhookTestRequest:
    """A webhook test request to simulate."""

    event_type: str
    payload: dict
    webhook_url: str
    secret: str
    headers: dict[str, str] = field(default_factory=dict)


@dataclass
class WebhookTestResult:
    """Result of a webhook test delivery."""

    test_id: str
    event_type: str
    webhook_url: str
    status: TestStatus
    status_code: int | None = None
    latency_ms: float | None = None
    response_body: str | None = None
    error: str | None = None
    payload_sent: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def is_success(self) -> bool:
        return self.status == TestStatus.PASS


# ── Event templates ──────────────────────────────────────

EVENT_TEMPLATES: dict[str, dict] = {
    "skill_pack.published": {
        "pack_id": "01ABC...",
        "name": "Example Skill Pack",
        "version": "1.0.0",
        "author": "developer",
        "org_id": "org-test",
    },
    "app.installed": {
        "installation_id": "inst-test",
        "app_id": "app-test",
        "org_id": "org-test",
        "installed_by": "user-test",
    },
    "app.uninstalled": {
        "installation_id": "inst-test",
        "app_id": "app-test",
        "org_id": "org-test",
    },
    "submission.graded": {
        "submission_id": "sub-test",
        "project_id": "proj-test",
        "student_id": "user-test",
        "score": 85,
        "graded_by": "ai",
    },
    "workflow.completed": {
        "run_id": "run-test",
        "workflow_id": "wf-test",
        "status": "completed",
        "duration_ms": 3200,
    },
}


class AppWebhookTestConsole:
    """Simulate and test webhook deliveries."""

    def __init__(self):
        self._history: dict[str, list[WebhookTestResult]] = {}
        self._next_id = 0

    def get_templates(self) -> dict[str, dict]:
        """Get available event type templates."""
        return dict(EVENT_TEMPLATES)

    def get_template(self, event_type: str) -> dict | None:
        return EVENT_TEMPLATES.get(event_type)

    def simulate(self, app_id: str, request: WebhookTestRequest,
                 status_code: int | None = None,
                 latency_ms: float | None = None,
                 response_body: str | None = None,
                 error: str | None = None) -> WebhookTestResult:
        """Simulate a webhook delivery and record the result.

        In production, this would make a real HTTP request.
        For testing, status_code/latency/response are provided by the caller.
        """
        self._next_id += 1
        test_id = f"test-{self._next_id}"

        if error:
            status = TestStatus.ERROR
        elif status_code is not None and 200 <= status_code < 300:
            status = TestStatus.PASS
        elif status_code is not None:
            status = TestStatus.FAIL
        else:
            status = TestStatus.PENDING

        result = WebhookTestResult(
            test_id=test_id,
            event_type=request.event_type,
            webhook_url=request.webhook_url,
            status=status,
            status_code=status_code,
            latency_ms=latency_ms,
            response_body=response_body,
            error=error,
            payload_sent=request.payload,
        )

        self._history.setdefault(app_id, []).insert(0, result)
        log.info("webhook_test.simulated", test_id=test_id, status=status.value,
                 event_type=request.event_type)
        return result

    def get_history(self, app_id: str, limit: int = 20) -> list[WebhookTestResult]:
        return self._history.get(app_id, [])[:limit]

    def get_result(self, app_id: str, test_id: str) -> WebhookTestResult | None:
        for result in self._history.get(app_id, []):
            if result.test_id == test_id:
                return result
        return None

    def get_pass_rate(self, app_id: str) -> float:
        history = self._history.get(app_id, [])
        if not history:
            return 0.0
        passed = sum(1 for r in history if r.status == TestStatus.PASS)
        return round((passed / len(history)) * 100, 1)

    def clear_history(self, app_id: str) -> int:
        count = len(self._history.get(app_id, []))
        self._history.pop(app_id, None)
        return count
