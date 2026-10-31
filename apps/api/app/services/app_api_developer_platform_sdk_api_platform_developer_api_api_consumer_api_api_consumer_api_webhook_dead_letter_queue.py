"""Webhook Dead Letter Queue — store permanently failed webhook deliveries for inspection."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class DeadLetterEntry:
    entry_id: str
    webhook_id: str
    consumer_id: str
    event_type: str
    payload: str
    last_error: str
    attempts: int
    first_failed_at: datetime
    last_failed_at: datetime
    status: str = "pending"  # "pending", "requeued", "discarded"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookDeadLetterQueue:
    def __init__(self, max_entries: int = 10000) -> None:
        self._entries: dict[tuple[str, str], DeadLetterEntry] = {}
        self._max = max_entries

    def enqueue(self, installation_id: str, entry: DeadLetterEntry) -> DeadLetterEntry:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, entry.entry_id)
        entry.status = "pending"
        self._entries[key] = entry
        log.info("dlq_enqueued", installation_id=installation_id, entry_id=entry.entry_id, event=entry.event_type, attempts=entry.attempts)
        # Evict oldest if over limit
        inst_entries = [(k, e) for k, e in self._entries.items() if k[0] == installation_id]
        if len(inst_entries) > self._max:
            oldest = min(inst_entries, key=lambda x: x[1].first_failed_at)
            del self._entries[oldest[0]]
        return entry

    def get(self, installation_id: str, entry_id: str) -> DeadLetterEntry | None:
        return self._entries.get((installation_id, entry_id))

    def requeue(self, installation_id: str, entry_id: str) -> DeadLetterEntry:
        key = (installation_id, entry_id)
        entry = self._entries.get(key)
        if not entry:
            raise ValueError("Entry not found")
        entry.status = "requeued"
        return entry

    def discard(self, installation_id: str, entry_id: str) -> DeadLetterEntry:
        key = (installation_id, entry_id)
        entry = self._entries.get(key)
        if not entry:
            raise ValueError("Entry not found")
        entry.status = "discarded"
        return entry

    def list_pending(self, installation_id: str, consumer_id: str | None = None, limit: int = 50) -> list[DeadLetterEntry]:
        entries = [e for (inst, _), e in self._entries.items() if inst == installation_id and e.status == "pending"]
        if consumer_id:
            entries = [e for e in entries if e.consumer_id == consumer_id]
        return sorted(entries, key=lambda e: e.last_failed_at, reverse=True)[:limit]

    def count(self, installation_id: str) -> dict[str, int]:
        entries = [e for (inst, _), e in self._entries.items() if inst == installation_id]
        return {"pending": sum(1 for e in entries if e.status == "pending"), "requeued": sum(1 for e in entries if e.status == "requeued"), "discarded": sum(1 for e in entries if e.status == "discarded")}
