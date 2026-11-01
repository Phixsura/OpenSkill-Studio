"""App API SDK Changelog — track SDK version changelogs."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class SDKChangelogEntry:
    version: str
    changes: list[str]
    breaking: bool = False

class AppAPISDKChangelog:
    def __init__(self) -> None:
        self._entries: dict[str, list[SDKChangelogEntry]] = {}

    def add_entry(self, installation_id: str, version: str, changes: list[str], breaking: bool = False) -> SDKChangelogEntry:
        if not installation_id: raise ValueError("installation_id is required")
        if not changes: raise ValueError("at least one change required")
        e = SDKChangelogEntry(version=version, changes=changes, breaking=breaking)
        self._entries.setdefault(installation_id, []).append(e)
        return e

    def latest(self, installation_id: str) -> SDKChangelogEntry | None:
        entries = self._entries.get(installation_id, [])
        return entries[-1] if entries else None

    def breaking_versions(self, installation_id: str) -> list[SDKChangelogEntry]:
        return [e for e in self._entries.get(installation_id, []) if e.breaking]

    def list_entries(self, installation_id: str) -> list[SDKChangelogEntry]:
        return list(reversed(self._entries.get(installation_id, [])))
