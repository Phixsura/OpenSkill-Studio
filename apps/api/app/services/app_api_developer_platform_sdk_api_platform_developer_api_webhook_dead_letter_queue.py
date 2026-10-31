"""API Webhook Dead Letter Queue — store failed webhook deliveries for retry/inspection."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class DeadLetterEntry:
    entry_id: str
    event_id: str
    consumer_id: str
    endpoint: str
    payload_preview: str  # truncated
    last_status_code: int
    attempts: int
    reason: str  # "max_retries", "timeout", "connection_error", "invalid_response"
    created_at: float = field(default_factory=time.time)
    requeued: bool = False

VALID_REASONS = {"max_retries", "timeout", "connection_error", "invalid_response", "circuit_open"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookDeadLetterQueue:
    def __init__(self, max_entries: int = 5000) -> None:
        self._queue: dict[str, list[DeadLetterEntry]] = {}
        self._max = max(100, max_entries)

    def enqueue(self, installation_id: str, entry: DeadLetterEntry) -> DeadLetterEntry:
        if not installation_id: raise ValueError("installation_id is required")
        if entry.reason not in VALID_REASONS: raise ValueError(f"Invalid reason: {entry.reason}")
        if len(entry.payload_preview) > 1024:
            entry.payload_preview = entry.payload_preview[:1024] + "...[TRUNCATED]"
        entries = self._queue.setdefault(installation_id, [])
        entries.append(entry)
        if len(entries) > self._max:
            self._queue[installation_id] = entries[-self._max:]
        return entry

    def requeue(self, installation_id: str, entry_id: str) -> DeadLetterEntry:
        entries = self._queue.get(installation_id, [])
        for e in entries:
            if e.entry_id == entry_id:
                if e.requeued: raise ValueError("Already requeued")
                e.requeued = True
                return e
        raise KeyError(f"Entry {entry_id} not found")

    def list_entries(self, installation_id: str, consumer_id: str | None = None, reason: str | None = None, limit: int = 50) -> list[DeadLetterEntry]:
        entries = self._queue.get(installation_id, [])
        if consumer_id: entries = [e for e in entries if e.consumer_id == consumer_id]
        if reason: entries = [e for e in entries if e.reason == reason]
        return list(reversed(entries[-limit:]))

    def purge(self, installation_id: str, consumer_id: str | None = None) -> int:
        if consumer_id:
            entries = self._queue.get(installation_id, [])
            before = len(entries)
            self._queue[installation_id] = [e for e in entries if e.consumer_id != consumer_id]
            return before - len(self._queue[installation_id])
        count = len(self._queue.get(installation_id, []))
        self._queue[installation_id] = []
        return count

    def count(self, installation_id: str) -> int:
        return len(self._queue.get(installation_id, []))

    def by_reason(self, installation_id: str) -> dict[str, int]:
        entries = self._queue.get(installation_id, [])
        counts: dict[str, int] = {}
        for e in entries: counts[e.reason] = counts.get(e.reason, 0) + 1
        return counts
