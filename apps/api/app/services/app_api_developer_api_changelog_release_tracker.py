"""App API Developer Changelog Release Tracker — track release cadence."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ReleaseInfo:
    version: str
    release_date: str
    entry_count: int
    breaking_count: int = 0

class AppAPIDeveloperAPIChangelogReleaseTracker:
    def __init__(self) -> None:
        self._releases: dict[str, list[ReleaseInfo]] = {}

    def track(self, installation_id: str, version: str, release_date: str, entry_count: int, breaking_count: int = 0) -> ReleaseInfo:
        if not installation_id: raise ValueError("installation_id is required")
        r = ReleaseInfo(version=version, release_date=release_date, entry_count=entry_count, breaking_count=breaking_count)
        self._releases.setdefault(installation_id, []).append(r)
        return r

    def release_count(self, installation_id: str) -> int:
        return len(self._releases.get(installation_id, []))

    def latest(self, installation_id: str) -> ReleaseInfo | None:
        releases = self._releases.get(installation_id, [])
        return releases[-1] if releases else None

    def total_entries(self, installation_id: str) -> int:
        return sum(r.entry_count for r in self._releases.get(installation_id, []))

    def list_releases(self, installation_id: str) -> list[ReleaseInfo]:
        return list(reversed(self._releases.get(installation_id, [])))
