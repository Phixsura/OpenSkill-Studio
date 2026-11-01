"""API Consumer Webhook Log — structured log of all webhook deliveries."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class WebhookLogEntry:
    log_id: str
    consumer_id: str
    event_type: str
    endpoint: str
    status_code: int
    duration_ms: float
    attempt: int = 1
    success: bool = True
    error_message: str = ""
    timestamp: float = field(default_factory=time.time)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerWebhookLog:
    def __init__(self, max_entries: int = 10000) -> None:
        self._logs: dict[str, list[WebhookLogEntry]] = {}
        self._max = max(100, max_entries)

    def record(self, installation_id: str, entry: WebhookLogEntry) -> WebhookLogEntry:
        if not installation_id: raise ValueError("installation_id is required")
        entries = self._logs.setdefault(installation_id, [])
        entries.append(entry)
        if len(entries) > self._max:
            self._logs[installation_id] = entries[-self._max:]
        return entry

    def query(self, installation_id: str, consumer_id: str | None = None, event_type: str | None = None, success: bool | None = None, limit: int = 50) -> list[WebhookLogEntry]:
        entries = self._logs.get(installation_id, [])
        if consumer_id: entries = [e for e in entries if e.consumer_id == consumer_id]
        if event_type: entries = [e for e in entries if e.event_type == event_type]
        if success is not None: entries = [e for e in entries if e.success == success]
        return list(reversed(entries[-limit:]))

    def delivery_stats(self, installation_id: str) -> dict[str, object]:
        entries = self._logs.get(installation_id, [])
        if not entries: return {"total": 0, "success": 0, "failed": 0, "success_rate": 0.0, "avg_duration_ms": 0.0}
        success = sum(1 for e in entries if e.success)
        failed = len(entries) - success
        avg_dur = round(sum(e.duration_ms for e in entries) / len(entries), 2)
        return {"total": len(entries), "success": success, "failed": failed, "success_rate": round((success / len(entries)) * 100, 1), "avg_duration_ms": avg_dur}

    def failed_deliveries(self, installation_id: str, limit: int = 20) -> list[WebhookLogEntry]:
        return self.query(installation_id, success=False, limit=limit)

    def count(self, installation_id: str) -> int:
        return len(self._logs.get(installation_id, []))
