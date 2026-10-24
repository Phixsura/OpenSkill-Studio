"""Webhook delivery tracker — track delivery status and retries."""
from __future__ import annotations


class WebhookDeliveryTracker:
    def __init__(self, max_retries: int = 3):
        self._max_retries = max_retries
        self._deliveries: list[dict] = []

    def record(self, webhook_id: str, url: str, status_code: int, attempt: int) -> dict:
        success = 200 <= status_code < 300
        should_retry = not success and attempt < self._max_retries
        entry = {"webhook_id": webhook_id, "url": url, "status_code": status_code,
                 "attempt": attempt, "success": success, "should_retry": should_retry}
        self._deliveries.append(entry)
        return entry

    def stats(self) -> dict:
        total = len(self._deliveries)
        successes = sum(1 for d in self._deliveries if d["success"])
        failures = total - successes
        rate = round(successes / max(total, 1) * 100, 1)
        return {"total": total, "successes": successes, "failures": failures,
                "success_rate": rate, "max_retries": self._max_retries}

    def failed_webhooks(self) -> list[dict]:
        failed: dict[str, dict] = {}
        for d in self._deliveries:
            if not d["success"]:
                wid = d["webhook_id"]
                if wid not in failed or d["attempt"] > failed[wid]["attempt"]:
                    failed[wid] = d
        return sorted(failed.values(), key=lambda x: -x["attempt"])
