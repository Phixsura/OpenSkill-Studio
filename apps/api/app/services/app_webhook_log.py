"""App Webhook Log — log webhook delivery attempts.

Logs webhook deliveries:
- Record each delivery attempt with response
- Query by status, destination, or event
- Retention-based cleanup
- Per-installation scoped logs
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class WebhookLogEntry:
    """A webhook delivery log entry."""

    log_id: str
    event_type: str
    destination: str
    status_code: int
    success: bool
    duration_ms: float
    request_size: int = 0
    response_preview: str = ""
    timestamp: float = field(default_factory=time.time)


class AppWebhookLog:
    """Log webhook delivery attempts."""

    def __init__(self, max_entries: int = 5000) -> None:
        self._max = max(1, max_entries)
        self._logs: dict[str, list[WebhookLogEntry]] = {}

    def record(
        self, installation_id: str, log_id: str, event_type: str,
        destination: str, status_code: int, duration_ms: float,
        request_size: int = 0, response_preview: str = "",
    ) -> WebhookLogEntry:
        if not installation_id:
            raise ValueError("installation_id is required")

        entry = WebhookLogEntry(
            log_id=log_id, event_type=event_type,
            destination=destination, status_code=status_code,
            success=200 <= status_code < 300,
            duration_ms=duration_ms, request_size=request_size,
            response_preview=response_preview[:500],  # truncate preview
        )
        entries = self._logs.setdefault(installation_id, [])
        entries.append(entry)
        if len(entries) > self._max:
            self._logs[installation_id] = entries[-self._max:]
        return entry

    def recent(self, installation_id: str, limit: int = 50) -> list[WebhookLogEntry]:
        return list(reversed(self._logs.get(installation_id, [])[-limit:]))

    def by_status(self, installation_id: str, success: bool) -> list[WebhookLogEntry]:
        return [e for e in self._logs.get(installation_id, []) if e.success == success]

    def by_event(self, installation_id: str, event_type: str) -> list[WebhookLogEntry]:
        return [e for e in self._logs.get(installation_id, []) if e.event_type == event_type]

    def success_rate(self, installation_id: str) -> float:
        entries = self._logs.get(installation_id, [])
        if not entries:
            return 100.0
        successes = sum(1 for e in entries if e.success)
        return round(successes / len(entries) * 100, 1)

    def count(self, installation_id: str) -> int:
        return len(self._logs.get(installation_id, []))
