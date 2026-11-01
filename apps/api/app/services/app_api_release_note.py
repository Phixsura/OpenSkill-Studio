"""App API Release Note — manage structured release notes.

Manages release notes:
- Create notes per version with sections
- Track highlights and known issues
- Per-installation scoped notes
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class ReleaseNote:
    """A structured release note."""

    note_id: str
    version: str
    title: str
    highlights: list[str] = field(default_factory=list)
    known_issues: list[str] = field(default_factory=list)
    published: bool = False


class AppAPIReleaseNote:
    """Manage structured release notes."""

    def __init__(self) -> None:
        self._notes: dict[tuple[str, str], ReleaseNote] = {}

    def create(
        self, installation_id: str, note_id: str, version: str, title: str,
        highlights: list[str] | None = None, known_issues: list[str] | None = None,
    ) -> ReleaseNote:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, note_id)
        if key in self._notes:
            raise ValueError(f"Note {note_id} already exists")

        note = ReleaseNote(
            note_id=note_id, version=version, title=title,
            highlights=highlights or [], known_issues=known_issues or [],
        )
        self._notes[key] = note
        return note

    def publish(self, installation_id: str, note_id: str) -> ReleaseNote:
        n = self._get(installation_id, note_id)
        n.published = True
        return n

    def published_notes(self, installation_id: str) -> list[ReleaseNote]:
        return [n for (inst, _), n in self._notes.items() if inst == installation_id and n.published]

    def list_notes(self, installation_id: str) -> list[ReleaseNote]:
        return [n for (inst, _), n in self._notes.items() if inst == installation_id]

    def _get(self, installation_id: str, note_id: str) -> ReleaseNote:
        key = (installation_id, note_id)
        n = self._notes.get(key)
        if n is None:
            raise KeyError(f"Note {note_id} not found")
        return n
