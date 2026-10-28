"""App API Changelog Diff — compare changes between versions.

Manages changelog diffs:
- Record changes (added/removed/modified) per version pair
- Summarize diff statistics
- Per-installation scoped diffs
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class DiffChange:
    """A single change in a diff."""

    change_type: str  # "added", "removed", "modified"
    path: str
    description: str = ""


@dataclass
class VersionDiff:
    """Diff between two versions."""

    diff_id: str
    from_version: str
    to_version: str
    changes: list[DiffChange] = field(default_factory=list)

    @property
    def summary(self) -> dict[str, int]:
        counts: dict[str, int] = {"added": 0, "removed": 0, "modified": 0}
        for c in self.changes:
            counts[c.change_type] = counts.get(c.change_type, 0) + 1
        return counts


class AppAPIChangelogDiff:
    """Compare changes between versions."""

    def __init__(self) -> None:
        self._diffs: dict[tuple[str, str], VersionDiff] = {}

    def create_diff(
        self, installation_id: str, diff_id: str,
        from_version: str, to_version: str, changes: list[dict],
    ) -> VersionDiff:
        if not installation_id:
            raise ValueError("installation_id is required")

        change_objs = [
            DiffChange(
                change_type=c["type"], path=c["path"],
                description=c.get("description", ""),
            )
            for c in changes
        ]
        diff = VersionDiff(
            diff_id=diff_id, from_version=from_version,
            to_version=to_version, changes=change_objs,
        )
        self._diffs[(installation_id, diff_id)] = diff
        return diff

    def get_diff(self, installation_id: str, diff_id: str) -> VersionDiff:
        key = (installation_id, diff_id)
        d = self._diffs.get(key)
        if d is None:
            raise KeyError(f"Diff {diff_id} not found")
        return d

    def list_diffs(self, installation_id: str) -> list[VersionDiff]:
        return [d for (inst, _), d in self._diffs.items() if inst == installation_id]
