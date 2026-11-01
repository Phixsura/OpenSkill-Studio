"""Webhook delivery log — immutable log of all webhook deliveries."""
from __future__ import annotations
from collections import defaultdict


class WebhookDeliveryLog:
    def __init__(self):
        self._log: list[dict] = []

    def record(self, webhook_id: str, url: str, status_code: int,
               duration_ms: float, attempt: int) -> dict:
        entry = {"webhook_id": webhook_id, "url": url, "status_code": status_code,
                 "duration_ms": duration_ms, "attempt": attempt,
                 "success": 200 <= status_code < 300}
        self._log.append(entry)
        return entry

    def by_webhook(self, webhook_id: str) -> list[dict]:
        return [e for e in self._log if e["webhook_id"] == webhook_id]

    def failure_rate(self) -> dict:
        if not self._log:
            return {"rate": 0, "total": 0}
        failures = sum(1 for e in self._log if not e["success"])
        return {"rate": round(failures / len(self._log) * 100, 1),
                "failures": failures, "total": len(self._log)}

    def slow_deliveries(self, threshold_ms: float = 5000) -> list[dict]:
        return [e for e in self._log if e["duration_ms"] > threshold_ms]

    def stats(self) -> dict:
        by_status: dict[int, int] = defaultdict(int)
        for e in self._log:
            by_status[e["status_code"]] += 1
        return {"total": len(self._log), "by_status": dict(by_status)}
