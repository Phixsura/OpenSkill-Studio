"""Changelog Parser — parse and query extension changelogs in Keep a Changelog format.

Parses markdown changelogs into structured releases with sections
(Added/Changed/Deprecated/Removed/Fixed/Security), supports version
comparison, breaking change detection, and release note generation.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field


@dataclass
class ChangelogEntry:
    description: str
    category: str  # Added, Changed, Fixed, etc.
    is_breaking: bool = False


@dataclass
class Release:
    version: str
    date: str
    entries: list[ChangelogEntry] = field(default_factory=list)
    yanked: bool = False

    @property
    def has_breaking_changes(self) -> bool:
        return any(e.is_breaking for e in self.entries)

    @property
    def by_category(self) -> dict[str, list[str]]:
        result: dict[str, list[str]] = {}
        for e in self.entries:
            result.setdefault(e.category, []).append(e.description)
        return result


VALID_CATEGORIES = {"Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"}
VERSION_RE = re.compile(r"^##\s+\[?(\d+\.\d+\.\d+(?:-[\w.]+)?)]?\s*(?:-\s*(.+))?$")
CATEGORY_RE = re.compile(r"^###\s+(\w+)\s*$")
ENTRY_RE = re.compile(r"^[-*]\s+(.+)$")
BREAKING_MARKERS = {"BREAKING", "BREAKING CHANGE", "⚠"}


class ChangelogParserService:
    """Parses Keep a Changelog format into structured releases."""

    def parse(self, content: str) -> list[Release]:
        releases: list[Release] = []
        current_release: Release | None = None
        current_category = ""

        for line in content.split("\n"):
            line = line.strip()
            if not line:
                continue

            # Version header
            vm = VERSION_RE.match(line)
            if vm:
                version = vm.group(1)
                date = vm.group(2) or ""
                yanked = "[YANKED]" in line.upper()
                current_release = Release(version=version, date=date.strip(), yanked=yanked)
                releases.append(current_release)
                current_category = ""
                continue

            # Category header
            cm = CATEGORY_RE.match(line)
            if cm and cm.group(1) in VALID_CATEGORIES:
                current_category = cm.group(1)
                continue

            # Entry
            em = ENTRY_RE.match(line)
            if em and current_release and current_category:
                desc = em.group(1)
                is_breaking = any(m in desc.upper() for m in BREAKING_MARKERS)
                current_release.entries.append(ChangelogEntry(
                    description=desc, category=current_category,
                    is_breaking=is_breaking,
                ))

        return releases

    def get_release(self, releases: list[Release], version: str) -> Release | None:
        return next((r for r in releases if r.version == version), None)

    def get_changes_between(self, releases: list[Release],
                            from_version: str, to_version: str) -> list[ChangelogEntry]:
        versions = [r.version for r in releases]
        try:
            from_idx = versions.index(from_version)
            to_idx = versions.index(to_version)
        except ValueError:
            return []
        start, end = min(from_idx, to_idx), max(from_idx, to_idx)
        entries: list[ChangelogEntry] = []
        for r in releases[start:end]:
            entries.extend(r.entries)
        return entries

    def has_breaking_between(self, releases: list[Release],
                             from_version: str, to_version: str) -> bool:
        changes = self.get_changes_between(releases, from_version, to_version)
        return any(e.is_breaking for e in changes)

    def generate_summary(self, release: Release) -> str:
        lines = [f"## {release.version}" + (f" - {release.date}" if release.date else "")]
        if release.yanked:
            lines.append("**⚠ This release has been yanked.**")
        for cat, entries in release.by_category.items():
            lines.append(f"### {cat}")
            for e in entries:
                lines.append(f"- {e}")
        return "\n".join(lines)
