"""App Changelog Compare — compare changelogs between two versions.

Compares changelog entries between version ranges:
- Entries added in newer version
- Category distribution comparison
- Breaking change summary
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class ChangelogEntry:
    """A changelog entry."""

    entry_id: str
    version: str
    title: str
    category: str
    breaking: bool = False


@dataclass
class VersionComparison:
    """Comparison between two version ranges."""

    from_version: str
    to_version: str
    new_entries: list[ChangelogEntry]
    category_counts: dict[str, int]
    breaking_count: int
    total_new: int


class AppChangelogCompare:
    """Compare changelogs between versions."""

    def __init__(self) -> None:
        # installation_id → list[ChangelogEntry]
        self._entries: dict[str, list[ChangelogEntry]] = {}

    def add_entry(
        self,
        installation_id: str,
        entry_id: str,
        version: str,
        title: str,
        category: str = "changed",
        breaking: bool = False,
    ) -> ChangelogEntry:
        if not installation_id:
            raise ValueError("installation_id is required")
        entry = ChangelogEntry(
            entry_id=entry_id, version=version,
            title=title, category=category, breaking=breaking,
        )
        self._entries.setdefault(installation_id, []).append(entry)
        return entry

    def compare(
        self,
        installation_id: str,
        from_version: str,
        to_version: str,
    ) -> VersionComparison:
        """Get all entries between from_version (exclusive) and to_version (inclusive)."""
        if not from_version or not to_version:
            raise ValueError("both versions required")

        entries = self._entries.get(installation_id, [])
        # Collect all unique versions in order
        versions = sorted(set(e.version for e in entries))

        try:
            from_idx = versions.index(from_version)
        except ValueError:
            from_idx = -1

        try:
            to_idx = versions.index(to_version)
        except ValueError:
            to_idx = len(versions) - 1

        target_versions = set(versions[from_idx + 1: to_idx + 1])
        new_entries = [e for e in entries if e.version in target_versions]

        cats: dict[str, int] = {}
        for e in new_entries:
            cats[e.category] = cats.get(e.category, 0) + 1

        return VersionComparison(
            from_version=from_version, to_version=to_version,
            new_entries=new_entries, category_counts=cats,
            breaking_count=sum(1 for e in new_entries if e.breaking),
            total_new=len(new_entries),
        )
