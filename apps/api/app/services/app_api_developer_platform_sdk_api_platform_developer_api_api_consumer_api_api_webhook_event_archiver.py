"""API Consumer Webhook Event Archiver — archive webhook events for compliance."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class ArchivedEvent:
    event_id: str
    event_type: str
    consumer_id: str
    payload_hash: str
    archived_at: float = field(default_factory=time.time)
    retention_days: int = 90
    size_bytes: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventArchiver:
    def __init__(self, max_archive_size: int = 100000) -> None:
        self._archive: dict[str, list[ArchivedEvent]] = {}
        self._max = max(1000, max_archive_size)

    def archive(self, installation_id: str, event: ArchivedEvent) -> ArchivedEvent:
        if not installation_id: raise ValueError("installation_id is required")
        if event.retention_days < 1: raise ValueError("retention must be >= 1 day")
        entries = self._archive.setdefault(installation_id, [])
        entries.append(event)
        if len(entries) > self._max: self._archive[installation_id] = entries[-self._max:]
        return event

    def search(self, installation_id: str, event_type: str | None = None, consumer_id: str | None = None, limit: int = 50) -> list[ArchivedEvent]:
        entries = self._archive.get(installation_id, [])
        if event_type: entries = [e for e in entries if e.event_type == event_type]
        if consumer_id: entries = [e for e in entries if e.consumer_id == consumer_id]
        return list(reversed(entries[-limit:]))

    def total_archived(self, installation_id: str) -> int:
        return len(self._archive.get(installation_id, []))

    def total_size_bytes(self, installation_id: str) -> int:
        return sum(e.size_bytes for e in self._archive.get(installation_id, []))

    def purge_expired(self, installation_id: str) -> int:
        now = time.time()
        entries = self._archive.get(installation_id, [])
        before = len(entries)
        self._archive[installation_id] = [e for e in entries if (now - e.archived_at) < e.retention_days * 86400]
        return before - len(self._archive[installation_id])
