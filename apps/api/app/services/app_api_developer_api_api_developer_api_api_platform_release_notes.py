"""App API Developer Platform Release Notes — versioned release note management."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class ReleaseNote:
    version: str
    title: str
    summary: str
    highlights: list[str] = field(default_factory=list)
    breaking_changes: list[str] = field(default_factory=list)
    published: bool = False
    published_at: float | None = None

class AppAPIDeveloperAPIApiDeveloperApiApiPlatformReleaseNotes:
    def __init__(self) -> None:
        self._notes: dict[tuple[str, str], ReleaseNote] = {}

    def create(self, installation_id: str, version: str, title: str, summary: str, highlights: list[str] | None = None, breaking_changes: list[str] | None = None) -> ReleaseNote:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, version)
        if key in self._notes: raise ValueError(f"Release {version} exists")
        n = ReleaseNote(version=version, title=title, summary=summary, highlights=highlights or [], breaking_changes=breaking_changes or [])
        self._notes[key] = n
        return n

    def publish(self, installation_id: str, version: str) -> ReleaseNote:
        n = self._get(installation_id, version)
        n.published = True
        n.published_at = time.time()
        return n

    def latest(self, installation_id: str) -> ReleaseNote | None:
        published = [n for (inst, _), n in self._notes.items() if inst == installation_id and n.published]
        return max(published, key=lambda n: n.published_at or 0) if published else None

    def all_notes(self, installation_id: str) -> list[ReleaseNote]:
        return [n for (inst, _), n in self._notes.items() if inst == installation_id]

    def with_breaking(self, installation_id: str) -> list[ReleaseNote]:
        return [n for (inst, _), n in self._notes.items() if inst == installation_id and n.breaking_changes]

    def _get(self, installation_id: str, version: str) -> ReleaseNote:
        key = (installation_id, version)
        n = self._notes.get(key)
        if n is None: raise KeyError(f"Release {version} not found")
        return n
