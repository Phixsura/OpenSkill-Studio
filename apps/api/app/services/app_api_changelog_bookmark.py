"""App API Changelog Bookmark — bookmark changelog entries for later."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class Bookmark:
    entry_id: str
    developer_id: str
    note: str = ""

class AppAPIChangelogBookmark:
    def __init__(self) -> None:
        self._bookmarks: dict[tuple[str, str, str], Bookmark] = {}

    def add(self, installation_id: str, developer_id: str, entry_id: str, note: str = "") -> Bookmark:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, developer_id, entry_id)
        b = Bookmark(entry_id=entry_id, developer_id=developer_id, note=note)
        self._bookmarks[key] = b
        return b

    def remove(self, installation_id: str, developer_id: str, entry_id: str) -> bool:
        key = (installation_id, developer_id, entry_id)
        if key in self._bookmarks:
            del self._bookmarks[key]
            return True
        return False

    def list_bookmarks(self, installation_id: str, developer_id: str) -> list[Bookmark]:
        return [b for (inst, dev, _), b in self._bookmarks.items() if inst == installation_id and dev == developer_id]

    def is_bookmarked(self, installation_id: str, developer_id: str, entry_id: str) -> bool:
        return (installation_id, developer_id, entry_id) in self._bookmarks
