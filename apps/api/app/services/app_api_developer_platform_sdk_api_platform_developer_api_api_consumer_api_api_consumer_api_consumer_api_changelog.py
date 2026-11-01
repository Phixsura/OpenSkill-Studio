"""Consumer API Changelog — track per-consumer API changes and notifications."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class ChangelogEntry:
    entry_id: str
    version: str
    title: str
    description: str
    change_type: str = "feature"  # "feature", "fix", "deprecation", "breaking", "security"
    published_at: datetime | None = None
    affected_endpoints: list[str] = field(default_factory=list)

@dataclass
class ReadStatus:
    consumer_id: str
    last_read_entry_id: str | None = None
    last_read_at: datetime | None = None

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiChangelog:
    def __init__(self) -> None:
        self._entries: dict[tuple[str, str], ChangelogEntry] = {}
        self._read_status: dict[tuple[str, str], ReadStatus] = {}
        self._order: dict[str, list[str]] = {}  # inst -> [entry_ids] in order

    def publish(self, installation_id: str, entry: ChangelogEntry) -> ChangelogEntry:
        if not installation_id:
            raise ValueError("installation_id is required")
        if entry.change_type not in ("feature", "fix", "deprecation", "breaking", "security"):
            raise ValueError(f"Invalid change_type: {entry.change_type}")
        entry.published_at = entry.published_at or datetime.utcnow()
        self._entries[(installation_id, entry.entry_id)] = entry
        if installation_id not in self._order:
            self._order[installation_id] = []
        if entry.entry_id not in self._order[installation_id]:
            self._order[installation_id].append(entry.entry_id)
        log.info("changelog_published", installation_id=installation_id, entry_id=entry.entry_id, type=entry.change_type)
        return entry

    def list_entries(self, installation_id: str, change_type: str | None = None, limit: int = 20) -> list[ChangelogEntry]:
        ids = self._order.get(installation_id, [])
        entries = [self._entries[(installation_id, eid)] for eid in reversed(ids)]
        if change_type:
            entries = [e for e in entries if e.change_type == change_type]
        return entries[:limit]

    def mark_read(self, installation_id: str, consumer_id: str, entry_id: str, now: datetime | None = None) -> ReadStatus:
        now = now or datetime.utcnow()
        status = ReadStatus(consumer_id=consumer_id, last_read_entry_id=entry_id, last_read_at=now)
        self._read_status[(installation_id, consumer_id)] = status
        return status

    def unread_count(self, installation_id: str, consumer_id: str) -> int:
        status = self._read_status.get((installation_id, consumer_id))
        ids = self._order.get(installation_id, [])
        if not status or not status.last_read_entry_id:
            return len(ids)
        try:
            idx = ids.index(status.last_read_entry_id)
            return len(ids) - idx - 1
        except ValueError:
            return len(ids)
