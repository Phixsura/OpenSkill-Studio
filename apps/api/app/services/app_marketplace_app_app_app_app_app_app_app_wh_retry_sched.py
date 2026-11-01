"""Webhook retry scheduler — schedule retries with exponential backoff."""
from __future__ import annotations
import time


class WebhookRetryScheduler:
    def __init__(self, max_retries: int = 5, base_delay_ms: int = 1000):
        self._max_retries = max_retries
        self._base_delay = base_delay_ms
        self._pending: list[dict] = []
        self._completed: list[dict] = []

    def schedule_retry(self, webhook_id: str, attempt: int, url: str) -> dict:
        if attempt >= self._max_retries:
            return {"scheduled": False, "webhook_id": webhook_id, "reason": "max_retries"}
        delay = self._base_delay * (2 ** attempt)
        retry = {"webhook_id": webhook_id, "attempt": attempt + 1,
                 "url": url, "delay_ms": delay,
                 "scheduled_at": time.time()}
        self._pending.append(retry)
        return {"scheduled": True, "delay_ms": delay, "next_attempt": attempt + 1}

    def complete(self, webhook_id: str, success: bool) -> dict:
        self._pending = [p for p in self._pending if p["webhook_id"] != webhook_id]
        self._completed.append({"webhook_id": webhook_id, "success": success})
        return {"webhook_id": webhook_id, "success": success}

    def stats(self) -> dict:
        succeeded = sum(1 for c in self._completed if c["success"])
        return {"pending": len(self._pending), "completed": len(self._completed),
                "succeeded": succeeded, "failed": len(self._completed) - succeeded}
