"""App API Changelog Archive — archive old changelog entries."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ArchivedEntry:
    entry_id: str
    title: str
    version: str
    archived: bool = False

class AppAPIChangelogArchive:
    def __init__(self) -> None:
        self._entries: dict[tuple[str, str], ArchivedEntry] = {}

    def add_entry(self, installation_id: str, entry_id: str, title: str, version: str) -> ArchivedEntry:
        if not installation_id: raise ValueError("installation_id is required")
        e = ArchivedEntry(entry_id=entry_id, title=title, version=version)
        self._entries[(installation_id, entry_id)] = e
        return e

    def archive(self, installation_id: str, entry_id: str) -> ArchivedEntry:
        e = self._entries.get((installation_id, entry_id))
        if e is None: raise KeyError(f"Entry {entry_id} not found")
        e.archived = True
        return e

    def active_entries(self, installation_id: str) -> list[ArchivedEntry]:
        return [e for (inst, _), e in self._entries.items() if inst == installation_id and not e.archived]

    def archived_entries(self, installation_id: str) -> list[ArchivedEntry]:
        return [e for (inst, _), e in self._entries.items() if inst == installation_id and e.archived]

    def list_all(self, installation_id: str) -> list[ArchivedEntry]:
        return [e for (inst, _), e in self._entries.items() if inst == installation_id]
