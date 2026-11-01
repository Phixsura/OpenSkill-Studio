"""App Changelog Generator — build structured changelogs from release entries.

Generates changelogs for app releases:
- Categorized entries (added, changed, fixed, removed, security, deprecated)
- Semantic version ordering
- Markdown rendering
- Breaking change flagging
- Per-app isolated changelogs
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class ChangeCategory(str, Enum):
    ADDED = "added"
    CHANGED = "changed"
    FIXED = "fixed"
    REMOVED = "removed"
    SECURITY = "security"
    DEPRECATED = "deprecated"


@dataclass
class ChangeEntry:
    """A single changelog entry."""

    description: str
    category: ChangeCategory
    breaking: bool = False
    author: str = ""


@dataclass
class ReleaseLog:
    """A versioned release with changelog entries."""

    version: str
    date: str  # ISO date string
    entries: list[ChangeEntry] = field(default_factory=list)
    summary: str = ""


_SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:-(.+))?$")


def _parse_semver(v: str) -> tuple[int, int, int, str]:
    m = _SEMVER_RE.match(v)
    if not m:
        return (0, 0, 0, v)
    pre = m.group(4) or ""
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)), pre)


class AppChangelogGenerator:
    """Build structured changelogs from release entries."""

    def __init__(self) -> None:
        # app_id → list[ReleaseLog]
        self._releases: dict[str, list[ReleaseLog]] = {}

    def add_release(
        self,
        app_id: str,
        version: str,
        date: str,
        summary: str = "",
    ) -> ReleaseLog:
        """Create a new release."""
        if not app_id:
            raise ValueError("app_id is required")
        if not version:
            raise ValueError("version is required")
        if not date:
            raise ValueError("date is required")

        releases = self._releases.setdefault(app_id, [])
        # Check duplicate version
        for r in releases:
            if r.version == version:
                raise ValueError(f"Version {version} already exists")

        release = ReleaseLog(version=version, date=date, summary=summary)
        releases.append(release)
        return release

    def add_entry(
        self,
        app_id: str,
        version: str,
        description: str,
        category: ChangeCategory,
        breaking: bool = False,
        author: str = "",
    ) -> ChangeEntry:
        """Add a changelog entry to a release."""
        release = self._find_release(app_id, version)
        if not description:
            raise ValueError("description is required")

        entry = ChangeEntry(
            description=description,
            category=category,
            breaking=breaking,
            author=author,
        )
        release.entries.append(entry)
        return entry

    def get_release(self, app_id: str, version: str) -> ReleaseLog:
        return self._find_release(app_id, version)

    def list_releases(self, app_id: str, limit: int = 20) -> list[ReleaseLog]:
        """List releases sorted by semver descending."""
        releases = self._releases.get(app_id, [])
        sorted_releases = sorted(
            releases,
            key=lambda r: _parse_semver(r.version),
            reverse=True,
        )
        return sorted_releases[:limit]

    def has_breaking_changes(self, app_id: str, version: str) -> bool:
        """Check if a release contains breaking changes."""
        release = self._find_release(app_id, version)
        return any(e.breaking for e in release.entries)

    def render_markdown(self, app_id: str, limit: int = 10) -> str:
        """Render changelog as Markdown."""
        releases = self.list_releases(app_id, limit=limit)
        if not releases:
            return "# Changelog\n\nNo releases yet.\n"

        lines = ["# Changelog\n"]
        for release in releases:
            header = f"## [{release.version}] — {release.date}"
            if self.has_breaking_changes(app_id, release.version):
                header += " ⚠️ BREAKING"
            lines.append(header)

            if release.summary:
                lines.append(f"\n{release.summary}\n")

            # Group by category
            by_cat: dict[ChangeCategory, list[ChangeEntry]] = {}
            for entry in release.entries:
                by_cat.setdefault(entry.category, []).append(entry)

            for cat in ChangeCategory:
                entries = by_cat.get(cat, [])
                if not entries:
                    continue
                lines.append(f"\n### {cat.value.capitalize()}\n")
                for e in entries:
                    prefix = "**BREAKING:** " if e.breaking else ""
                    lines.append(f"- {prefix}{e.description}")

            lines.append("")

        return "\n".join(lines)

    def get_stats(self, app_id: str) -> dict[str, int]:
        """Get entry count by category across all releases."""
        releases = self._releases.get(app_id, [])
        stats: dict[str, int] = {cat.value: 0 for cat in ChangeCategory}
        for r in releases:
            for e in r.entries:
                stats[e.category.value] += 1
        return stats

    def _find_release(self, app_id: str, version: str) -> ReleaseLog:
        releases = self._releases.get(app_id, [])
        for r in releases:
            if r.version == version:
                return r
        raise KeyError(f"Release {version} not found for app {app_id}")
