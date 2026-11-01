"""Consumer Webhook Log — structured log of all webhook delivery attempts."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class WebhookLogEntry:
    log_id: str
    webhook_id: str
    consumer_id: str
    event_type: str
    url: str
    method: str = "POST"
    request_headers: dict[str, str] = field(default_factory=dict)
    response_status: int | None = None
    response_time_ms: float = 0.0
    attempt: int = 1
    success: bool = False
    error_message: str | None = None
    timestamp: datetime | None = None

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerWebhookLog:
    def __init__(self, max_entries_per_consumer: int = 10000) -> None:
        self._logs: dict[tuple[str, str], list[WebhookLogEntry]] = {}
        self._max = max_entries_per_consumer

    def record(self, installation_id: str, entry: WebhookLogEntry) -> WebhookLogEntry:
        if not installation_id:
            raise ValueError("installation_id is required")
        entry.timestamp = entry.timestamp or datetime.utcnow()
        # Redact sensitive headers
        safe_headers = {k: ("***" if k.lower() in ("authorization", "x-api-key") else v) for k, v in entry.request_headers.items()}
        entry.request_headers = safe_headers
        key = (installation_id, entry.consumer_id)
        if key not in self._logs:
            self._logs[key] = []
        self._logs[key].append(entry)
        if len(self._logs[key]) > self._max:
            self._logs[key] = self._logs[key][-self._max:]
        return entry

    def query(self, installation_id: str, consumer_id: str, event_type: str | None = None, success: bool | None = None, limit: int = 50) -> list[WebhookLogEntry]:
        entries = self._logs.get((installation_id, consumer_id), [])
        if event_type is not None:
            entries = [e for e in entries if e.event_type == event_type]
        if success is not None:
            entries = [e for e in entries if e.success == success]
        return entries[-limit:]

    def failure_rate(self, installation_id: str, consumer_id: str) -> float:
        entries = self._logs.get((installation_id, consumer_id), [])
        if not entries:
            return 0.0
        return sum(1 for e in entries if not e.success) / len(entries)

    def avg_response_time(self, installation_id: str, consumer_id: str) -> float:
        entries = self._logs.get((installation_id, consumer_id), [])
        successful = [e for e in entries if e.success and e.response_time_ms > 0]
        if not successful:
            return 0.0
        return sum(e.response_time_ms for e in successful) / len(successful)
