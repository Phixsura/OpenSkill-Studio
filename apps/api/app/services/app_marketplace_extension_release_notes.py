"""Release Notes — structured release notes with rich formatting.

Generates release notes from features/fixes/breaking changes,
supports audience targeting (users vs developers), and highlights.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ReleaseNote:
    version: str
    title: str
    summary: str
    features: list[str] = field(default_factory=list)
    fixes: list[str] = field(default_factory=list)
    breaking: list[str] = field(default_factory=list)
    highlights: list[str] = field(default_factory=list)
    contributors: list[str] = field(default_factory=list)


class ExtensionReleaseNotesService:
    """Manages structured release notes."""

    def __init__(self):
        self._notes: dict[str, list[ReleaseNote]] = {}

    def create(self, extension_id: str, version: str, title: str,
               summary: str, features: list[str] | None = None,
               fixes: list[str] | None = None,
               breaking: list[str] | None = None,
               highlights: list[str] | None = None,
               contributors: list[str] | None = None) -> ReleaseNote:
        note = ReleaseNote(
            version=version, title=title, summary=summary,
            features=features or [], fixes=fixes or [],
            breaking=breaking or [], highlights=highlights or [],
            contributors=contributors or [],
        )
        self._notes.setdefault(extension_id, []).append(note)
        return note

    def get_latest(self, extension_id: str) -> ReleaseNote | None:
        notes = self._notes.get(extension_id, [])
        return notes[-1] if notes else None

    def get_all(self, extension_id: str) -> list[ReleaseNote]:
        return list(self._notes.get(extension_id, []))

    def render_markdown(self, note: ReleaseNote) -> str:
        lines = [f"# {note.title}", "", f"**{note.version}**", "", note.summary, ""]
        if note.highlights:
            lines.append("## 🌟 Highlights")
            for h in note.highlights:
                lines.append(f"- {h}")
            lines.append("")
        if note.breaking:
            lines.append("## ⚠️ Breaking Changes")
            for b in note.breaking:
                lines.append(f"- {b}")
            lines.append("")
        if note.features:
            lines.append("## ✨ New Features")
            for f in note.features:
                lines.append(f"- {f}")
            lines.append("")
        if note.fixes:
            lines.append("## 🐛 Bug Fixes")
            for f in note.fixes:
                lines.append(f"- {f}")
            lines.append("")
        if note.contributors:
            lines.append(f"## 🙏 Contributors: {', '.join(note.contributors)}")
        return "\n".join(lines)

    def render_user_summary(self, note: ReleaseNote) -> str:
        parts = []
        if note.highlights:
            parts.append("Highlights: " + "; ".join(note.highlights))
        if note.features:
            parts.append(f"{len(note.features)} new features")
        if note.fixes:
            parts.append(f"{len(note.fixes)} bug fixes")
        if note.breaking:
            parts.append(f"⚠️ {len(note.breaking)} breaking changes")
        return " · ".join(parts) if parts else note.summary
