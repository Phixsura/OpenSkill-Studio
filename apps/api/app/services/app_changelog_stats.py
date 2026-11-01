"""App Changelog Stats — aggregate statistics across all changelogs.

Computes aggregate statistics:
- Total releases, entries, breaking changes
- Most active contributors
- Release cadence (avg days between releases)
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class ChangelogStats:
    """Aggregate changelog statistics."""

    total_releases: int
    total_entries: int
    breaking_changes: int
    categories: dict[str, int]
    top_contributors: list[tuple[str, int]]
    avg_days_between_releases: float


@dataclass
class ReleaseData:
    """Input data for a release."""

    version: str
    timestamp: float
    entry_count: int
    breaking_count: int
    categories: dict[str, int]
    contributors: list[str]


class AppChangelogStats:
    """Compute aggregate changelog statistics."""

    def __init__(self) -> None:
        self._releases: dict[str, list[ReleaseData]] = {}

    def add_release(
        self,
        installation_id: str,
        release: ReleaseData,
    ) -> None:
        if not installation_id:
            raise ValueError("installation_id is required")
        self._releases.setdefault(installation_id, []).append(release)

    def compute(self, installation_id: str) -> ChangelogStats:
        releases = self._releases.get(installation_id, [])
        if not releases:
            return ChangelogStats(
                total_releases=0, total_entries=0, breaking_changes=0,
                categories={}, top_contributors=[], avg_days_between_releases=0,
            )

        total_entries = sum(r.entry_count for r in releases)
        breaking = sum(r.breaking_count for r in releases)

        cats: dict[str, int] = {}
        contrib_counts: dict[str, int] = {}
        for r in releases:
            for cat, count in r.categories.items():
                cats[cat] = cats.get(cat, 0) + count
            for c in r.contributors:
                contrib_counts[c] = contrib_counts.get(c, 0) + 1

        top = sorted(contrib_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        sorted_releases = sorted(releases, key=lambda r: r.timestamp)
        if len(sorted_releases) >= 2:
            gaps = [
                (sorted_releases[i + 1].timestamp - sorted_releases[i].timestamp) / 86400
                for i in range(len(sorted_releases) - 1)
            ]
            avg_cadence = round(sum(gaps) / len(gaps), 1)
        else:
            avg_cadence = 0

        return ChangelogStats(
            total_releases=len(releases),
            total_entries=total_entries,
            breaking_changes=breaking,
            categories=cats,
            top_contributors=top,
            avg_days_between_releases=avg_cadence,
        )
