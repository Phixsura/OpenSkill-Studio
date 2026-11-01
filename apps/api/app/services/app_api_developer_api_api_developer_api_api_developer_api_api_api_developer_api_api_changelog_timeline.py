"""App API Developer API Changelog Timeline — chronological API change timeline."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class ChangelogTimelineEntry:
    entry_id: str
    version: str
    title: str
    change_type: str  # "feature", "fix", "breaking", "deprecation", "security"
    timestamp: float = field(default_factory=time.time)

class AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiChangelogTimeline:
    def __init__(self) -> None:
        self._entries: dict[str, list[ChangelogTimelineEntry]] = {}

    def add(self, installation_id: str, entry_id: str, version: str, title: str, change_type: str) -> ChangelogTimelineEntry:
        if not installation_id: raise ValueError("installation_id is required")
        valid = {"feature", "fix", "breaking", "deprecation", "security"}
        if change_type not in valid: raise ValueError("invalid change_type")
        e = ChangelogTimelineEntry(entry_id=entry_id, version=version, title=title, change_type=change_type)
        self._entries.setdefault(installation_id, []).append(e)
        return e

    def timeline(self, installation_id: str, limit: int = 20) -> list[ChangelogTimelineEntry]:
        return list(reversed(self._entries.get(installation_id, [])[-limit:]))

    def by_type(self, installation_id: str, change_type: str) -> list[ChangelogTimelineEntry]:
        return [e for e in self._entries.get(installation_id, []) if e.change_type == change_type]

    def by_version(self, installation_id: str, version: str) -> list[ChangelogTimelineEntry]:
        return [e for e in self._entries.get(installation_id, []) if e.version == version]

    def type_counts(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for e in self._entries.get(installation_id, []):
            counts[e.change_type] = counts.get(e.change_type, 0) + 1
        return counts
