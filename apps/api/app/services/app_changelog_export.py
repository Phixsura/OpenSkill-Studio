"""App Changelog Export — export changelogs in multiple formats.

Exports changelogs for installed apps:
- Markdown export
- JSON export
- CSV export
- Filtered by version range
"""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class ExportEntry:
    """An entry to export."""

    version: str
    date: str
    title: str
    category: str
    breaking: bool = False


@dataclass
class ExportResult:
    """Result of an export."""

    format: str
    content: str
    entry_count: int


class AppChangelogExport:
    """Export changelogs in multiple formats."""

    def __init__(self) -> None:
        self._entries: dict[str, list[ExportEntry]] = {}

    def add_entry(
        self, installation_id: str, entry: ExportEntry
    ) -> None:
        if not installation_id:
            raise ValueError("installation_id is required")
        self._entries.setdefault(installation_id, []).append(entry)

    def export_markdown(self, installation_id: str) -> ExportResult:
        entries = self._entries.get(installation_id, [])
        lines = ["# Changelog\n"]
        by_version: dict[str, list[ExportEntry]] = {}
        for e in entries:
            by_version.setdefault(e.version, []).append(e)

        for ver in sorted(by_version, reverse=True):
            items = by_version[ver]
            date = items[0].date if items else ""
            lines.append(f"\n## [{ver}] — {date}\n")
            for e in items:
                prefix = "**BREAKING:** " if e.breaking else ""
                lines.append(f"- {prefix}{e.title}")

        return ExportResult(format="markdown", content="\n".join(lines), entry_count=len(entries))

    def export_json(self, installation_id: str) -> ExportResult:
        entries = self._entries.get(installation_id, [])
        data = [
            {"version": e.version, "date": e.date, "title": e.title,
             "category": e.category, "breaking": e.breaking}
            for e in entries
        ]
        return ExportResult(format="json", content=json.dumps(data, indent=2), entry_count=len(entries))

    def export_csv(self, installation_id: str) -> ExportResult:
        entries = self._entries.get(installation_id, [])
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["version", "date", "title", "category", "breaking"])
        for e in entries:
            writer.writerow([e.version, e.date, e.title, e.category, e.breaking])
        return ExportResult(format="csv", content=buf.getvalue(), entry_count=len(entries))
