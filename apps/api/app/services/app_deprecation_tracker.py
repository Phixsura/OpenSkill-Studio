"""App Deprecation Tracker — manage API deprecation lifecycle.

Tracks deprecated APIs and features:
- Mark endpoints as deprecated with sunset dates
- Migration guide references
- Track adoption of replacements
- Per-installation scoped deprecations
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class Deprecation:
    """A deprecated API or feature."""

    deprecation_id: str
    resource: str  # endpoint or feature name
    reason: str
    sunset_date: str  # ISO date
    replacement: str = ""  # suggested replacement
    migration_guide_url: str = ""
    usage_count: int = 0  # current usage of deprecated feature
    replacement_usage_count: int = 0


class AppDeprecationTracker:
    """Manage API deprecation lifecycle."""

    def __init__(self) -> None:
        # (installation_id, deprecation_id) → Deprecation
        self._deprecations: dict[tuple[str, str], Deprecation] = {}

    def deprecate(
        self,
        installation_id: str,
        deprecation_id: str,
        resource: str,
        reason: str,
        sunset_date: str,
        replacement: str = "",
        migration_guide_url: str = "",
    ) -> Deprecation:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not deprecation_id:
            raise ValueError("deprecation_id is required")
        if not resource:
            raise ValueError("resource is required")
        if not sunset_date:
            raise ValueError("sunset_date is required")

        key = (installation_id, deprecation_id)
        if key in self._deprecations:
            raise ValueError(f"Deprecation {deprecation_id} already exists")

        dep = Deprecation(
            deprecation_id=deprecation_id, resource=resource,
            reason=reason, sunset_date=sunset_date,
            replacement=replacement, migration_guide_url=migration_guide_url,
        )
        self._deprecations[key] = dep
        return dep

    def update_usage(
        self,
        installation_id: str,
        deprecation_id: str,
        usage_count: int = 0,
        replacement_usage_count: int = 0,
    ) -> Deprecation:
        dep = self._get(installation_id, deprecation_id)
        dep.usage_count = max(0, usage_count)
        dep.replacement_usage_count = max(0, replacement_usage_count)
        return dep

    def migration_progress(self, installation_id: str, deprecation_id: str) -> float:
        """% of usage migrated to replacement."""
        dep = self._get(installation_id, deprecation_id)
        total = dep.usage_count + dep.replacement_usage_count
        if total == 0:
            return 100.0  # nothing to migrate
        return round(dep.replacement_usage_count / total * 100, 1)

    def list_deprecations(self, installation_id: str) -> list[Deprecation]:
        return [d for (inst, _), d in self._deprecations.items() if inst == installation_id]

    def get_deprecation(self, installation_id: str, deprecation_id: str) -> Deprecation:
        return self._get(installation_id, deprecation_id)

    def _get(self, installation_id: str, deprecation_id: str) -> Deprecation:
        key = (installation_id, deprecation_id)
        dep = self._deprecations.get(key)
        if dep is None:
            raise KeyError(f"Deprecation {deprecation_id} not found")
        return dep
