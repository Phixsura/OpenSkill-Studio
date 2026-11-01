"""Changelog Feed — aggregated changelog across all extensions."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class ChangelogEntry:
    entry_id: str
    extension_id: str
    version: str
    changes: list[str]
    change_type: str = "feature"  # feature, fix, breaking, deprecation
    published_at: float = 0.0
    def __post_init__(self):
        if not self.published_at: self.published_at = time.time()


class ChangelogFeedService:
    def __init__(self):
        self._entries: list[ChangelogEntry] = []
        self._counter = 0

    def publish(self, extension_id: str, version: str, changes: list[str],
                change_type: str = "feature") -> ChangelogEntry:
        self._counter += 1
        entry = ChangelogEntry(
            entry_id=f"cl-{self._counter}", extension_id=extension_id,
            version=version, changes=changes, change_type=change_type)
        self._entries.append(entry)
        return entry

    def get_feed(self, limit: int = 50, change_type: str | None = None,
                 extension_id: str | None = None) -> list[ChangelogEntry]:
        entries = sorted(self._entries, key=lambda e: e.published_at, reverse=True)
        if change_type:
            entries = [e for e in entries if e.change_type == change_type]
        if extension_id:
            entries = [e for e in entries if e.extension_id == extension_id]
        return entries[:limit]

    def get_breaking_changes(self) -> list[ChangelogEntry]:
        return [e for e in self._entries if e.change_type == "breaking"]

    def count_by_type(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for e in self._entries:
            counts[e.change_type] = counts.get(e.change_type, 0) + 1
        return counts
