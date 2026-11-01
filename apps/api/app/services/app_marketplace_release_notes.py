"""Release Notes — generate rich release notes for extension versions.

Combines changelog entries, dependency changes, migration notes,
and highlights into formatted release notes for marketplace display.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ReleaseHighlight:
    title: str
    description: str
    icon: str = "✨"


@dataclass
class ReleaseNotes:
    extension_id: str
    version: str
    summary: str
    highlights: list[ReleaseHighlight] = field(default_factory=list)
    changes: dict[str, list[str]] = field(default_factory=dict)  # type -> [messages]
    breaking_changes: list[str] = field(default_factory=list)
    dependency_updates: list[dict] = field(default_factory=list)
    migration_notes: str = ""
    contributors: list[str] = field(default_factory=list)


class ReleaseNotesGenerator:
    """Generates formatted release notes from structured data."""

    def __init__(self):
        self._releases: dict[str, ReleaseNotes] = {}

    def create(self, notes: ReleaseNotes) -> ReleaseNotes:
        key = f"{notes.extension_id}@{notes.version}"
        self._releases[key] = notes
        return notes

    def get(self, extension_id: str, version: str) -> ReleaseNotes | None:
        return self._releases.get(f"{extension_id}@{version}")

    def render_markdown(self, notes: ReleaseNotes) -> str:
        """Render release notes as markdown."""
        lines = [f"# {notes.extension_id} v{notes.version}", "", notes.summary, ""]

        if notes.highlights:
            lines.append("## Highlights")
            lines.append("")
            for h in notes.highlights:
                lines.append(f"### {h.icon} {h.title}")
                lines.append(f"{h.description}")
                lines.append("")

        if notes.breaking_changes:
            lines.append("## ⚠️ Breaking Changes")
            lines.append("")
            for bc in notes.breaking_changes:
                lines.append(f"- {bc}")
            lines.append("")

        type_labels = {"feat": "Features", "fix": "Bug Fixes", "perf": "Performance",
                       "docs": "Documentation", "refactor": "Refactoring"}
        for change_type in ["feat", "fix", "perf", "docs", "refactor"]:
            changes = notes.changes.get(change_type, [])
            if changes:
                label = type_labels.get(change_type, change_type)
                lines.append(f"## {label}")
                lines.append("")
                for c in changes:
                    lines.append(f"- {c}")
                lines.append("")

        if notes.dependency_updates:
            lines.append("## Dependency Updates")
            lines.append("")
            for dep in notes.dependency_updates:
                lines.append(f"- **{dep['name']}**: {dep.get('from', '?')} → {dep.get('to', '?')}")
            lines.append("")

        if notes.migration_notes:
            lines.append("## Migration Guide")
            lines.append("")
            lines.append(notes.migration_notes)
            lines.append("")

        if notes.contributors:
            lines.append(f"## Contributors")
            lines.append("")
            lines.append(", ".join(f"@{c}" for c in notes.contributors))

        return "\n".join(lines)

    def render_summary(self, notes: ReleaseNotes) -> dict:
        total_changes = sum(len(v) for v in notes.changes.values())
        return {
            "version": notes.version,
            "summary": notes.summary,
            "highlights": len(notes.highlights),
            "total_changes": total_changes,
            "breaking_changes": len(notes.breaking_changes),
            "dependency_updates": len(notes.dependency_updates),
            "has_migration": bool(notes.migration_notes),
            "contributors": len(notes.contributors),
        }
