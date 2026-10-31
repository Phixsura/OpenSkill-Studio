"""App Webhook Delivery Log — track webhook delivery attempts and responses.

Records webhook delivery attempts with full request/response details:
- Track delivery status (success, failed, pending)
- Response status codes and timing
- Retry attempt tracking
- Per-installation scoped delivery logs
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class DeliveryAttempt:
    """A single webhook delivery attempt."""

    attempt_id: str
    webhook_id: str
    installation_id: str
    url: str
    event_type: str
    status_code: int | None = None
    success: bool = False
    response_time_ms: float = 0.0
    attempt_number: int = 1
    error: str = ""
    timestamp: float = field(default_factory=time.time)


class AppWebhookDeliveryLog:
    """Track webhook delivery attempts and responses."""

    def __init__(self, max_entries: int = 5000) -> None:
        self._attempts: list[DeliveryAttempt] = []
        self._max = max(100, max_entries)

    def record_attempt(
        self,
        installation_id: str,
        attempt_id: str,
        webhook_id: str,
        url: str,
        event_type: str,
        status_code: int | None = None,
        success: bool = False,
        response_time_ms: float = 0.0,
        attempt_number: int = 1,
        error: str = "",
        now: float | None = None,
    ) -> DeliveryAttempt:
        """Record a delivery attempt."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not webhook_id:
            raise ValueError("webhook_id is required")
        if not url:
            raise ValueError("url is required")

        attempt = DeliveryAttempt(
            attempt_id=attempt_id,
            webhook_id=webhook_id,
            installation_id=installation_id,
            url=url,
            event_type=event_type,
            status_code=status_code,
            success=success,
            response_time_ms=max(0.0, response_time_ms),
            attempt_number=attempt_number,
            error=error,
            timestamp=now or time.time(),
        )
        self._attempts.append(attempt)
        if len(self._attempts) > self._max:
            self._attempts = self._attempts[-self._max:]
        return attempt

    def get_attempts(
        self,
        installation_id: str,
        webhook_id: str | None = None,
        success_only: bool | None = None,
        limit: int = 50,
    ) -> list[DeliveryAttempt]:
        """Query delivery attempts, newest first."""
        if not installation_id:
            raise ValueError("installation_id is required")
        results = [a for a in self._attempts if a.installation_id == installation_id]
        if webhook_id:
            results = [a for a in results if a.webhook_id == webhook_id]
        if success_only is not None:
            results = [a for a in results if a.success == success_only]
        return list(reversed(results[-limit:]))

    def get_success_rate(self, installation_id: str) -> float:
        """Overall success rate percentage."""
        attempts = [a for a in self._attempts if a.installation_id == installation_id]
        if not attempts:
            return 100.0
        successes = sum(1 for a in attempts if a.success)
        return round(successes / len(attempts) * 100, 2)

    def get_avg_response_time(self, installation_id: str) -> float:
        """Average response time in ms for successful deliveries."""
        successful = [
            a for a in self._attempts
            if a.installation_id == installation_id and a.success
        ]
        if not successful:
            return 0.0
        return round(sum(a.response_time_ms for a in successful) / len(successful), 2)

    def count(self, installation_id: str) -> int:
        return sum(1 for a in self._attempts if a.installation_id == installation_id)
