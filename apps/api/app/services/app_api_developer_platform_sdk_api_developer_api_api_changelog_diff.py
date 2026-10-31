"""App API Developer API Changelog Diff — compare changes between API versions."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ChangeEntry:
    change_type: str  # "added", "removed", "modified", "deprecated"
    target: str  # endpoint or field path
    description: str

@dataclass
class VersionDiff:
    from_version: str
    to_version: str
    changes: list[ChangeEntry] = field(default_factory=list)

    @property
    def breaking_count(self) -> int:
        return sum(1 for c in self.changes if c.change_type in ("removed", "modified"))

    @property
    def additions(self) -> int:
        return sum(1 for c in self.changes if c.change_type == "added")

    @property
    def is_breaking(self) -> bool:
        return self.breaking_count > 0

class AppAPIDeveloperPlatformSDKApiDeveloperApiApiChangelogDiff:
    def __init__(self) -> None:
        self._diffs: dict[tuple[str, str, str], VersionDiff] = {}

    def create_diff(self, installation_id: str, from_version: str, to_version: str, changes: list[dict]) -> VersionDiff:
        if not installation_id: raise ValueError("installation_id is required")
        valid_types = {"added", "removed", "modified", "deprecated"}
        parsed = []
        for c in changes:
            if c["change_type"] not in valid_types: raise ValueError(f"Invalid type: {c['change_type']}")
            parsed.append(ChangeEntry(change_type=c["change_type"], target=c["target"], description=c["description"]))
        d = VersionDiff(from_version=from_version, to_version=to_version, changes=parsed)
        self._diffs[(installation_id, from_version, to_version)] = d
        return d

    def get_diff(self, installation_id: str, from_ver: str, to_ver: str) -> VersionDiff | None:
        return self._diffs.get((installation_id, from_ver, to_ver))

    def breaking_diffs(self, installation_id: str) -> list[VersionDiff]:
        return [d for (inst, _, _), d in self._diffs.items() if inst == installation_id and d.is_breaking]

    def all_diffs(self, installation_id: str) -> list[VersionDiff]:
        return [d for (inst, _, _), d in self._diffs.items() if inst == installation_id]
