"""API Consumer Changelog Feed — personalized changelog feeds per consumer."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class ChangelogEntry:
    entry_id: str
    version: str
    title: str
    change_type: str  # "feature", "fix", "deprecation", "breaking"
    description: str = ""
    affected_endpoints: list[str] = field(default_factory=list)
    published_at: float = field(default_factory=time.time)

@dataclass
class FeedItem:
    entry: ChangelogEntry
    relevant: bool = True  # relevant to consumer's subscribed endpoints
    read: bool = False

VALID_TYPES = {"feature", "fix", "deprecation", "breaking", "security", "improvement"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiChangelogFeed:
    def __init__(self) -> None:
        self._entries: dict[str, list[ChangelogEntry]] = {}
        self._read: dict[tuple[str, str, str], bool] = {}  # (inst, consumer, entry_id) → read

    def publish(self, installation_id: str, entry: ChangelogEntry) -> ChangelogEntry:
        if not installation_id: raise ValueError("installation_id is required")
        if entry.change_type not in VALID_TYPES: raise ValueError(f"Invalid type: {entry.change_type}")
        self._entries.setdefault(installation_id, []).append(entry)
        return entry

    def feed_for_consumer(self, installation_id: str, consumer_id: str, endpoints: list[str] | None = None, limit: int = 20) -> list[FeedItem]:
        entries = self._entries.get(installation_id, [])
        items: list[FeedItem] = []
        for e in reversed(entries[-limit:]):
            relevant = not endpoints or any(ep in e.affected_endpoints for ep in endpoints) or not e.affected_endpoints
            read = self._read.get((installation_id, consumer_id, e.entry_id), False)
            items.append(FeedItem(entry=e, relevant=relevant, read=read))
        return items

    def mark_read(self, installation_id: str, consumer_id: str, entry_id: str) -> None:
        self._read[(installation_id, consumer_id, entry_id)] = True

    def unread_count(self, installation_id: str, consumer_id: str) -> int:
        entries = self._entries.get(installation_id, [])
        return sum(1 for e in entries if not self._read.get((installation_id, consumer_id, e.entry_id), False))

    def entry_count(self, installation_id: str) -> int:
        return len(self._entries.get(installation_id, []))
