"""Version Manager — semantic versioning and release management for extensions.

Tracks extension versions, enforces semver ordering, manages
changelogs, and supports rollback to previous versions.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Version:
    major: int
    minor: int
    patch: int
    prerelease: str = ""

    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        return f"{base}-{self.prerelease}" if self.prerelease else base

    def __lt__(self, other: "Version") -> bool:
        if (self.major, self.minor, self.patch) != (other.major, other.minor, other.patch):
            return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
        if self.prerelease and not other.prerelease:
            return True  # prerelease < release
        return self.prerelease < other.prerelease


def parse_version(version_str: str) -> Version | None:
    """Parse a semver string into a Version object."""
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)(?:-(.+))?$", version_str)
    if not m:
        return None
    return Version(int(m[1]), int(m[2]), int(m[3]), m[4] or "")


@dataclass
class Release:
    version: Version
    changelog: str
    published_at: str
    size_bytes: int = 0
    downloads: int = 0
    yanked: bool = False


class VersionManager:
    """Manages versions and releases for extensions."""

    def __init__(self):
        self._releases: dict[str, list[Release]] = {}  # ext_id -> releases

    def publish_release(
        self, extension_id: str, version_str: str, changelog: str,
        size_bytes: int = 0,
    ) -> tuple[Release | None, str]:
        """Publish a new version. Must be higher than all existing versions."""
        version = parse_version(version_str)
        if not version:
            return None, f"Invalid version: {version_str}"

        releases = self._releases.get(extension_id, [])
        active = [r for r in releases if not r.yanked]
        if active and not all(r.version < version for r in active):
            return None, f"Version {version_str} must be higher than existing versions"

        release = Release(
            version=version, changelog=changelog,
            published_at=datetime.now(timezone.utc).isoformat(),
            size_bytes=size_bytes,
        )
        if extension_id not in self._releases:
            self._releases[extension_id] = []
        self._releases[extension_id].append(release)
        return release, "Published"

    def get_latest(self, extension_id: str) -> Release | None:
        releases = self._releases.get(extension_id, [])
        active = [r for r in releases if not r.yanked]
        return max(active, key=lambda r: r.version) if active else None

    def list_versions(self, extension_id: str, include_yanked: bool = False) -> list[Release]:
        releases = self._releases.get(extension_id, [])
        if not include_yanked:
            releases = [r for r in releases if not r.yanked]
        return sorted(releases, key=lambda r: r.version, reverse=True)

    def yank_version(self, extension_id: str, version_str: str) -> bool:
        """Yank (soft-delete) a specific version."""
        version = parse_version(version_str)
        if not version:
            return False
        for release in self._releases.get(extension_id, []):
            if str(release.version) == str(version):
                release.yanked = True
                return True
        return False

    def get_changelog(self, extension_id: str, version_str: str | None = None) -> str:
        """Get changelog for a specific version, or combined for all."""
        releases = self.list_versions(extension_id)
        if version_str:
            for r in releases:
                if str(r.version) == version_str:
                    return r.changelog
            return ""
        return "\n\n".join(f"## {r.version}\n{r.changelog}" for r in releases)
