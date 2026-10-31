"""Endpoint Changelog Manager — structured changelog with categorized entries."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = structlog.get_logger()

CHANGE_TYPES = ("added", "changed", "deprecated", "removed", "fixed", "security")


@dataclass
class ChangelogEntry:
    entry_id: str
    version: str
    change_type: str
    description: str
    endpoint_id: str = ""
    breaking: bool = False
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ChangelogManager:
    """Manage structured changelogs with categorized entries."""

    _entries: list[ChangelogEntry] = field(default_factory=list)

    def add_entry(self, entry: ChangelogEntry) -> dict:
        if entry.change_type not in CHANGE_TYPES:
            raise ValueError(f"Invalid type: {entry.change_type}. Must be one of {CHANGE_TYPES}")
        if not entry.description:
            raise ValueError("Description is required")
        self._entries.append(entry)
        logger.info("changelog_entry_added", entry_id=entry.entry_id, version=entry.version)
        return {"entry_id": entry.entry_id, "version": entry.version, "type": entry.change_type}

    def get_version(self, version: str) -> dict:
        entries = [e for e in self._entries if e.version == version]
        if not entries:
            return {"version": version, "entries": []}
        by_type: dict[str, list[dict]] = {}
        for e in entries:
            by_type.setdefault(e.change_type, []).append({
                "entry_id": e.entry_id, "description": e.description,
                "endpoint_id": e.endpoint_id, "breaking": e.breaking,
            })
        has_breaking = any(e.breaking for e in entries)
        return {
            "version": version,
            "entry_count": len(entries),
            "has_breaking_changes": has_breaking,
            "by_type": by_type,
        }

    def get_breaking_changes(self, since_version: str | None = None) -> list[dict]:
        entries = [e for e in self._entries if e.breaking]
        if since_version:
            entries = [e for e in entries if e.version >= since_version]
        return [
            {"version": e.version, "description": e.description,
             "endpoint_id": e.endpoint_id, "type": e.change_type}
            for e in entries
        ]

    def get_endpoint_history(self, endpoint_id: str) -> list[dict]:
        entries = [e for e in self._entries if e.endpoint_id == endpoint_id]
        return [
            {"version": e.version, "type": e.change_type,
             "description": e.description, "breaking": e.breaking}
            for e in reversed(entries)
        ]

    def list_versions(self) -> list[str]:
        versions = sorted(set(e.version for e in self._entries), reverse=True)
        return versions

    def generate_markdown(self, version: str) -> str:
        data = self.get_version(version)
        if not data["by_type"]:
            return f"## {version}\n\nNo entries.\n"
        lines = [f"## {version}\n"]
        for change_type in CHANGE_TYPES:
            entries = data["by_type"].get(change_type, [])
            if entries:
                lines.append(f"### {change_type.capitalize()}\n")
                for e in entries:
                    prefix = "**BREAKING** " if e["breaking"] else ""
                    lines.append(f"- {prefix}{e['description']}")
                lines.append("")
        return "\n".join(lines)

    def search(self, query: str) -> list[dict]:
        q = query.lower()
        return [
            {"entry_id": e.entry_id, "version": e.version,
             "type": e.change_type, "description": e.description}
            for e in self._entries if q in e.description.lower()
        ]

    def get_stats(self) -> dict:
        by_type = {}
        for t in CHANGE_TYPES:
            by_type[t] = sum(1 for e in self._entries if e.change_type == t)
        return {
            "total_entries": len(self._entries),
            "versions": len(set(e.version for e in self._entries)),
            "breaking_changes": sum(1 for e in self._entries if e.breaking),
            "by_type": by_type,
        }
