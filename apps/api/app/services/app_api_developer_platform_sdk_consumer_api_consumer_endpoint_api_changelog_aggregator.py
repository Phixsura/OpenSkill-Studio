"""Consumer API Changelog Aggregator — aggregate changelogs across all versions."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class ChangeEntry:
    entry_id: str
    version: str
    change_type: str  # "added", "changed", "deprecated", "removed", "fixed", "security"
    title: str
    description: str = ""
    breaking: bool = False
    published_at: datetime | None = None

@dataclass
class AggregatedChangelog:
    total_entries: int
    by_type: dict[str, int]
    breaking_count: int
    versions: list[str]
    recent_entries: list[ChangeEntry]

VALID_TYPES = {"added", "changed", "deprecated", "removed", "fixed", "security"}

class AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiChangelogAggregator:
    def __init__(self) -> None:
        self._entries: dict[tuple[str, str], ChangeEntry] = {}

    def add_entry(self, installation_id: str, entry: ChangeEntry) -> ChangeEntry:
        if not installation_id:
            raise ValueError("installation_id is required")
        if entry.change_type not in VALID_TYPES:
            raise ValueError(f"Invalid change_type: {entry.change_type}")
        entry.published_at = entry.published_at or datetime.utcnow()
        self._entries[(installation_id, entry.entry_id)] = entry
        return entry

    def aggregate(self, installation_id: str, limit: int = 20) -> AggregatedChangelog:
        entries = sorted([e for (inst, _), e in self._entries.items() if inst == installation_id], key=lambda e: e.published_at or datetime.min, reverse=True)
        by_type: dict[str, int] = {}
        versions: set[str] = set()
        breaking = 0
        for e in entries:
            by_type[e.change_type] = by_type.get(e.change_type, 0) + 1
            versions.add(e.version)
            if e.breaking:
                breaking += 1
        return AggregatedChangelog(total_entries=len(entries), by_type=by_type, breaking_count=breaking, versions=sorted(versions, reverse=True), recent_entries=entries[:limit])

    def get_by_version(self, installation_id: str, version: str) -> list[ChangeEntry]:
        return sorted([e for (inst, _), e in self._entries.items() if inst == installation_id and e.version == version], key=lambda e: e.published_at or datetime.min, reverse=True)

    def search(self, installation_id: str, query: str) -> list[ChangeEntry]:
        q = query.lower()
        return [e for (inst, _), e in self._entries.items() if inst == installation_id and (q in e.title.lower() or q in e.description.lower())]
