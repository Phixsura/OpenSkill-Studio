"""App API Changelog — track API endpoint changes between versions.

Tracks changes to API endpoints:
- Record added, modified, removed endpoints per version
- Breaking change detection
- Per-installation scoped endpoint tracking
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class EndpointChangeType(str, Enum):
    ADDED = "added"
    MODIFIED = "modified"
    REMOVED = "removed"
    DEPRECATED = "deprecated"


@dataclass
class EndpointChange:
    """A change to an API endpoint."""

    method: str
    path: str
    change_type: EndpointChangeType
    breaking: bool = False
    description: str = ""


@dataclass
class APIChangelog:
    """Changelog for API endpoints between versions."""

    from_version: str
    to_version: str
    changes: list[EndpointChange]

    @property
    def breaking_count(self) -> int:
        return sum(1 for c in self.changes if c.breaking)

    @property
    def added_count(self) -> int:
        return sum(1 for c in self.changes if c.change_type == EndpointChangeType.ADDED)

    @property
    def removed_count(self) -> int:
        return sum(1 for c in self.changes if c.change_type == EndpointChangeType.REMOVED)


class AppAPIChangelog:
    """Track API endpoint changes between versions."""

    def __init__(self) -> None:
        # (installation_id, from_ver, to_ver) → APIChangelog
        self._changelogs: dict[tuple[str, str, str], APIChangelog] = {}

    def record_changes(
        self,
        installation_id: str,
        from_version: str,
        to_version: str,
        changes: list[dict],
    ) -> APIChangelog:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not from_version or not to_version:
            raise ValueError("both versions required")

        change_objs = [
            EndpointChange(
                method=c["method"].upper(), path=c["path"],
                change_type=EndpointChangeType(c["change_type"]),
                breaking=c.get("breaking", False),
                description=c.get("description", ""),
            )
            for c in changes
        ]

        changelog = APIChangelog(
            from_version=from_version, to_version=to_version, changes=change_objs,
        )
        self._changelogs[(installation_id, from_version, to_version)] = changelog
        return changelog

    def get_changelog(
        self, installation_id: str, from_version: str, to_version: str
    ) -> APIChangelog:
        key = (installation_id, from_version, to_version)
        cl = self._changelogs.get(key)
        if cl is None:
            raise KeyError(f"No changelog for {from_version} → {to_version}")
        return cl

    def list_changelogs(self, installation_id: str) -> list[APIChangelog]:
        return [cl for (inst, _, _), cl in self._changelogs.items() if inst == installation_id]
