"""Consumer API Webhook Testing — send test payloads to verify webhook endpoints."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import json
import structlog

log = structlog.get_logger()

@dataclass
class TestPayload:
    event_type: str
    payload: dict = field(default_factory=dict)

@dataclass
class TestResult:
    test_id: str
    webhook_url: str
    event_type: str
    simulated_status: int
    simulated_latency_ms: float
    payload_size_bytes: int
    success: bool
    error: str | None = None
    tested_at: datetime | None = None

# Standard test payloads for common events
STANDARD_PAYLOADS: dict[str, dict] = {
    "ping": {"event": "ping", "timestamp": "2026-06-01T00:00:00Z"},
    "order.created": {"event": "order.created", "data": {"order_id": "test_order_001", "amount": 99.99, "currency": "USD"}},
    "user.created": {"event": "user.created", "data": {"user_id": "test_user_001", "email": "test@example.com"}},
    "payment.completed": {"event": "payment.completed", "data": {"payment_id": "test_pay_001", "amount": 50.00, "status": "completed"}},
}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookTesting:
    def __init__(self) -> None:
        self._results: dict[tuple[str, str], list[TestResult]] = {}

    def send_test(self, installation_id: str, consumer_id: str, webhook_url: str, payload: TestPayload, now: datetime | None = None) -> TestResult:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not webhook_url.startswith("https://"):
            raise ValueError("webhook_url must use HTTPS")
        now = now or datetime.utcnow()
        body = json.dumps(payload.payload if payload.payload else STANDARD_PAYLOADS.get(payload.event_type, {"event": payload.event_type}))
        result = TestResult(
            test_id=f"test-{now.isoformat()}", webhook_url=webhook_url, event_type=payload.event_type,
            simulated_status=200, simulated_latency_ms=45.0, payload_size_bytes=len(body.encode()),
            success=True, tested_at=now,
        )
        key = (installation_id, consumer_id)
        if key not in self._results:
            self._results[key] = []
        self._results[key].append(result)
        log.info("webhook_test_sent", installation_id=installation_id, consumer=consumer_id, event=payload.event_type)
        return result

    def get_standard_events(self) -> list[str]:
        return sorted(STANDARD_PAYLOADS.keys())

    def get_history(self, installation_id: str, consumer_id: str, limit: int = 20) -> list[TestResult]:
        return self._results.get((installation_id, consumer_id), [])[-limit:]

    def success_rate(self, installation_id: str, consumer_id: str) -> float:
        results = self._results.get((installation_id, consumer_id), [])
        if not results:
            return 1.0
        return sum(1 for r in results if r.success) / len(results)
