"""Consumer API Webhook Testing — webhook endpoint testing with mock payloads."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = structlog.get_logger()


@dataclass
class TestPayload:
    payload_id: str
    event_type: str
    body: dict
    description: str = ""


@dataclass
class TestResult:
    test_id: str
    webhook_url: str
    payload_id: str
    status_code: int
    response_body: str = ""
    latency_ms: float = 0.0
    success: bool = True
    error: str = ""
    tested_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class WebhookTester:
    """Test webhook endpoints with mock payloads and validate responses."""

    _payloads: dict[str, TestPayload] = field(default_factory=dict)
    _results: list[TestResult] = field(default_factory=list)

    def create_payload(self, payload: TestPayload) -> dict:
        if payload.payload_id in self._payloads:
            raise ValueError(f"Payload {payload.payload_id} already exists")
        if not payload.body:
            raise ValueError("Payload body is required")
        self._payloads[payload.payload_id] = payload
        logger.info("test_payload_created", payload_id=payload.payload_id)
        return {"payload_id": payload.payload_id, "event_type": payload.event_type}

    def run_test(self, test_id: str, webhook_url: str, payload_id: str,
                 simulated_status: int = 200, simulated_latency: float = 50.0,
                 simulated_error: str = "") -> dict:
        payload = self._payloads.get(payload_id)
        if not payload:
            raise ValueError(f"Payload {payload_id} not found")
        if not webhook_url.startswith("http"):
            raise ValueError("webhook_url must start with http")
        success = 200 <= simulated_status < 300 and not simulated_error
        result = TestResult(
            test_id=test_id, webhook_url=webhook_url, payload_id=payload_id,
            status_code=simulated_status, latency_ms=simulated_latency,
            success=success, error=simulated_error,
        )
        self._results.append(result)
        logger.info("webhook_test_run", test_id=test_id, success=success)
        return {
            "test_id": test_id, "success": success,
            "status_code": simulated_status, "latency_ms": simulated_latency,
            "error": simulated_error or None,
        }

    def run_suite(self, webhook_url: str, payload_ids: list[str] | None = None,
                  simulated_status: int = 200) -> dict:
        ids = payload_ids or list(self._payloads.keys())
        results = []
        for i, pid in enumerate(ids):
            tid = f"suite-{i+1}"
            r = self.run_test(tid, webhook_url, pid, simulated_status)
            results.append(r)
        passed = sum(1 for r in results if r["success"])
        return {
            "total": len(results), "passed": passed,
            "failed": len(results) - passed,
            "all_passed": passed == len(results),
        }

    def get_results(self, webhook_url: str | None = None, limit: int = 20) -> list[dict]:
        results = list(reversed(self._results))
        if webhook_url:
            results = [r for r in results if r.webhook_url == webhook_url]
        return [
            {"test_id": r.test_id, "webhook_url": r.webhook_url,
             "payload_id": r.payload_id, "success": r.success,
             "status_code": r.status_code, "latency_ms": r.latency_ms}
            for r in results[:limit]
        ]

    def list_payloads(self) -> list[dict]:
        return [
            {"payload_id": p.payload_id, "event_type": p.event_type,
             "description": p.description}
            for p in self._payloads.values()
        ]

    def get_stats(self) -> dict:
        total = len(self._results)
        passed = sum(1 for r in self._results if r.success)
        return {
            "total_payloads": len(self._payloads),
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": round(passed / total * 100, 1) if total > 0 else 0,
        }
