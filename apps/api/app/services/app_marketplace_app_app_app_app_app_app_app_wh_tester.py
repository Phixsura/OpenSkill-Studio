"""Webhook tester — send test events and verify endpoint responses."""
from __future__ import annotations
import secrets
import json


def build_test_event(event_type: str, *, app_id: str = "test_app") -> dict:
    return {
        "id": f"evt_test_{secrets.token_hex(4)}",
        "type": event_type, "test": True,
        "payload": {"app_id": app_id, "timestamp": "2026-10-24T12:00:00Z"},
    }


def evaluate_response(*, status_code: int, response_body: str,
                        latency_ms: int, timeout_ms: int = 5000) -> dict:
    timed_out = latency_ms >= timeout_ms
    success = 200 <= status_code < 300 and not timed_out
    is_json = False
    try:
        json.loads(response_body)
        is_json = True
    except (json.JSONDecodeError, TypeError):
        pass
    issues = []
    if timed_out:
        issues.append("Timed out")
    if status_code >= 400:
        issues.append(f"HTTP {status_code}")
    if not is_json and success:
        issues.append("Response is not JSON")
    return {"success": success, "status_code": status_code,
            "latency_ms": latency_ms, "timed_out": timed_out,
            "is_json": is_json, "issues": issues,
            "grade": "A" if success and latency_ms < 500 else "B" if success else "F"}
