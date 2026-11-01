"""Consumer API Release Note — manage per-version release notes."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class ReleaseNote:
    note_id: str
    version: str
    title: str
    body: str
    change_type: str = "feature"  # "feature", "fix", "improvement", "breaking", "security"
    published: bool = False
    published_at: datetime | None = None
    author: str = ""

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiReleaseNote:
    def __init__(self) -> None:
        self._notes: dict[tuple[str, str], ReleaseNote] = {}

    def create(self, installation_id: str, note: ReleaseNote) -> ReleaseNote:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not note.title:
            raise ValueError("title is required")
        if note.change_type not in ("feature", "fix", "improvement", "breaking", "security"):
            raise ValueError(f"Invalid change_type: {note.change_type}")
        key = (installation_id, note.note_id)
        if key in self._notes:
            raise ValueError(f"Note {note.note_id} already exists")
        self._notes[key] = note
        return note

    def publish(self, installation_id: str, note_id: str, now: datetime) -> ReleaseNote:
        key = (installation_id, note_id)
        note = self._notes.get(key)
        if not note:
            raise ValueError("Note not found")
        note.published = True
        note.published_at = now
        return note

    def list_by_version(self, installation_id: str, version: str) -> list[ReleaseNote]:
        return [n for (inst, _), n in self._notes.items() if inst == installation_id and n.version == version]

    def list_published(self, installation_id: str, limit: int = 20) -> list[ReleaseNote]:
        notes = [n for (inst, _), n in self._notes.items() if inst == installation_id and n.published]
        return sorted(notes, key=lambda n: n.published_at or datetime.min, reverse=True)[:limit]

    def search(self, installation_id: str, query: str) -> list[ReleaseNote]:
        q = query.lower()
        return [n for (inst, _), n in self._notes.items() if inst == installation_id and (q in n.title.lower() or q in n.body.lower())]
