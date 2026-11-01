"""App API Developer Webhook Event Log — searchable log of all webhook events."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class WebhookEventLogEntry:
    event_id: str
    event_type: str
    destination: str
    status: str  # "delivered", "failed", "pending", "retrying"
    payload_size_bytes: int
    timestamp: float = field(default_factory=time.time)

class AppAPIDeveloperAPIApiWebhookEventLog:
    def __init__(self, max_entries: int = 10000) -> None:
        self._max = max(1, max_entries)
        self._log: dict[str, list[WebhookEventLogEntry]] = {}

    def append(self, installation_id: str, event_id: str, event_type: str, destination: str, status: str, payload_size_bytes: int) -> WebhookEventLogEntry:
        if not installation_id: raise ValueError("installation_id is required")
        if status not in ("delivered", "failed", "pending", "retrying"): raise ValueError("invalid status")
        e = WebhookEventLogEntry(event_id=event_id, event_type=event_type, destination=destination, status=status, payload_size_bytes=payload_size_bytes)
        entries = self._log.setdefault(installation_id, [])
        entries.append(e)
        if len(entries) > self._max: self._log[installation_id] = entries[-self._max:]
        return e

    def search(self, installation_id: str, event_type: str | None = None, status: str | None = None, destination: str | None = None, limit: int = 50) -> list[WebhookEventLogEntry]:
        entries = self._log.get(installation_id, [])
        if event_type: entries = [e for e in entries if e.event_type == event_type]
        if status: entries = [e for e in entries if e.status == status]
        if destination: entries = [e for e in entries if e.destination == destination]
        return list(reversed(entries[-limit:]))

    def summary(self, installation_id: str) -> dict[str, int]:
        entries = self._log.get(installation_id, [])
        return {s: sum(1 for e in entries if e.status == s) for s in ("delivered", "failed", "pending", "retrying")}

    def total(self, installation_id: str) -> int:
        return len(self._log.get(installation_id, []))
