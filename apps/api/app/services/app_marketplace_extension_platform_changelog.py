"""Platform Changelog — track all platform-level changes.

Manages platform releases, breaking changes, deprecations, and
new feature announcements with version tracking.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class PlatformRelease:
    version: str
    date: str
    title: str
    features: list[str] = field(default_factory=list)
    fixes: list[str] = field(default_factory=list)
    breaking: list[str] = field(default_factory=list)
    deprecations: list[str] = field(default_factory=list)


class PlatformChangelogService:
    """Manages platform release changelog."""

    def __init__(self):
        self._releases: list[PlatformRelease] = []

    def add_release(self, version: str, date: str, title: str,
                    features: list[str] | None = None,
                    fixes: list[str] | None = None,
                    breaking: list[str] | None = None,
                    deprecations: list[str] | None = None) -> PlatformRelease:
        release = PlatformRelease(
            version=version, date=date, title=title,
            features=features or [], fixes=fixes or [],
            breaking=breaking or [], deprecations=deprecations or [],
        )
        self._releases.append(release)
        self._releases.sort(key=lambda r: r.version, reverse=True)
        return release

    def get_latest(self) -> PlatformRelease | None:
        return self._releases[0] if self._releases else None

    def get_all(self) -> list[PlatformRelease]:
        return list(self._releases)

    def get_breaking_changes(self) -> list[dict]:
        result = []
        for r in self._releases:
            for b in r.breaking:
                result.append({"version": r.version, "change": b})
        return result

    def search(self, query: str) -> list[PlatformRelease]:
        q = query.lower()
        return [r for r in self._releases
                if q in r.title.lower()
                or any(q in f.lower() for f in r.features + r.fixes)]

    def get_stats(self) -> dict:
        return {
            "total_releases": len(self._releases),
            "total_features": sum(len(r.features) for r in self._releases),
            "total_fixes": sum(len(r.fixes) for r in self._releases),
            "total_breaking": sum(len(r.breaking) for r in self._releases),
        }
