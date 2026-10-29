"""App API Developer Changelog Preview — preview changelogs before publishing."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ChangelogPreview:
    preview_id: str
    version: str
    title: str
    entries: list[str]
    published: bool = False
    reviewer: str = ""

class AppAPIDeveloperAPIChangelogPreview:
    def __init__(self) -> None:
        self._previews: dict[tuple[str, str], ChangelogPreview] = {}

    def create(self, installation_id: str, preview_id: str, version: str, title: str, entries: list[str]) -> ChangelogPreview:
        if not installation_id: raise ValueError("installation_id is required")
        if not entries: raise ValueError("at least one entry required")
        key = (installation_id, preview_id)
        if key in self._previews: raise ValueError(f"Preview {preview_id} exists")
        p = ChangelogPreview(preview_id=preview_id, version=version, title=title, entries=entries)
        self._previews[key] = p
        return p

    def approve(self, installation_id: str, preview_id: str, reviewer: str) -> ChangelogPreview:
        p = self._get(installation_id, preview_id)
        p.reviewer = reviewer
        return p

    def publish(self, installation_id: str, preview_id: str) -> ChangelogPreview:
        p = self._get(installation_id, preview_id)
        if not p.reviewer: raise ValueError("Must be approved before publishing")
        p.published = True
        return p

    def drafts(self, installation_id: str) -> list[ChangelogPreview]:
        return [p for (inst, _), p in self._previews.items() if inst == installation_id and not p.published]

    def list_previews(self, installation_id: str) -> list[ChangelogPreview]:
        return [p for (inst, _), p in self._previews.items() if inst == installation_id]

    def _get(self, installation_id: str, preview_id: str) -> ChangelogPreview:
        p = self._previews.get((installation_id, preview_id))
        if p is None: raise KeyError(f"Preview {preview_id} not found")
        return p
