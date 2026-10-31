"""App Compatibility Matrix — track platform version compatibility for installed apps.

Maps which app versions work with which platform versions:
- Compatibility declaration per app version
- Platform upgrade impact analysis (which apps break)
- App upgrade path finder (which version supports new platform)
- Compatibility status: compatible, degraded, incompatible, untested
- Matrix query by app or platform version
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class CompatStatus(str, Enum):
    COMPATIBLE = "compatible"
    DEGRADED = "degraded"
    INCOMPATIBLE = "incompatible"
    UNTESTED = "untested"


@dataclass
class CompatEntry:
    """Compatibility of one app version with one platform version."""

    app_id: str
    app_version: str
    platform_version: str
    status: CompatStatus
    notes: str = ""


@dataclass
class ImpactReport:
    """Impact of upgrading the platform to a new version."""

    platform_version: str
    compatible: list[CompatEntry]
    degraded: list[CompatEntry]
    incompatible: list[CompatEntry]
    untested: list[str]   # app_ids with no entry for this platform version
    safe_to_upgrade: bool


@dataclass
class UpgradePath:
    """Recommended app version to move to for a target platform."""

    app_id: str
    current_version: str
    target_platform: str
    recommended_version: str | None
    status: CompatStatus


class AppCompatibilityMatrix:
    """Track and query app ↔ platform version compatibility."""

    def __init__(self):
        # (app_id, app_version, platform_version) → CompatEntry
        self._entries: dict[tuple[str, str, str], CompatEntry] = {}
        # app_id → set of known versions
        self._app_versions: dict[str, set[str]] = {}

    def declare(self, app_id: str, app_version: str, platform_version: str,
                status: CompatStatus, notes: str = "") -> CompatEntry:
        """Declare compatibility for an app version + platform version pair."""
        entry = CompatEntry(
            app_id=app_id, app_version=app_version,
            platform_version=platform_version, status=status, notes=notes,
        )
        self._entries[(app_id, app_version, platform_version)] = entry
        self._app_versions.setdefault(app_id, set()).add(app_version)
        return entry

    def get(self, app_id: str, app_version: str,
            platform_version: str) -> CompatEntry | None:
        return self._entries.get((app_id, app_version, platform_version))

    def get_status(self, app_id: str, app_version: str,
                   platform_version: str) -> CompatStatus:
        entry = self.get(app_id, app_version, platform_version)
        return entry.status if entry else CompatStatus.UNTESTED

    # ── Platform upgrade impact ──────────────────────────

    def analyze_upgrade_impact(self, platform_version: str,
                               installed_apps: list[tuple[str, str]]) -> ImpactReport:
        """Analyze the impact of upgrading to a platform version.

        installed_apps: list of (app_id, current_app_version) tuples.
        """
        compatible: list[CompatEntry] = []
        degraded: list[CompatEntry] = []
        incompatible: list[CompatEntry] = []
        untested: list[str] = []

        for app_id, app_version in installed_apps:
            entry = self.get(app_id, app_version, platform_version)
            if entry is None:
                untested.append(app_id)
            elif entry.status == CompatStatus.COMPATIBLE:
                compatible.append(entry)
            elif entry.status == CompatStatus.DEGRADED:
                degraded.append(entry)
            elif entry.status == CompatStatus.INCOMPATIBLE:
                incompatible.append(entry)

        safe = len(incompatible) == 0 and len(untested) == 0

        return ImpactReport(
            platform_version=platform_version,
            compatible=compatible,
            degraded=degraded,
            incompatible=incompatible,
            untested=untested,
            safe_to_upgrade=safe,
        )

    # ── Upgrade path finder ──────────────────────────────

    def find_upgrade_path(self, app_id: str, current_version: str,
                          target_platform: str) -> UpgradePath:
        """Find the best app version compatible with a target platform."""
        # Check current version first
        current_status = self.get_status(app_id, current_version, target_platform)
        if current_status == CompatStatus.COMPATIBLE:
            return UpgradePath(
                app_id=app_id, current_version=current_version,
                target_platform=target_platform,
                recommended_version=current_version,
                status=CompatStatus.COMPATIBLE,
            )

        # Search other versions for a compatible one
        versions = self._app_versions.get(app_id, set())
        best: str | None = None
        best_status = CompatStatus.UNTESTED

        for ver in sorted(versions, reverse=True):  # newest first
            status = self.get_status(app_id, ver, target_platform)
            if status == CompatStatus.COMPATIBLE:
                best = ver
                best_status = status
                break
            elif status == CompatStatus.DEGRADED and best is None:
                best = ver
                best_status = status

        return UpgradePath(
            app_id=app_id, current_version=current_version,
            target_platform=target_platform,
            recommended_version=best,
            status=best_status if best else CompatStatus.INCOMPATIBLE,
        )

    # ── Matrix queries ───────────────────────────────────

    def get_app_matrix(self, app_id: str) -> list[CompatEntry]:
        """Get all compatibility entries for an app."""
        return sorted(
            [e for e in self._entries.values() if e.app_id == app_id],
            key=lambda e: (e.app_version, e.platform_version),
        )

    def get_platform_matrix(self, platform_version: str) -> list[CompatEntry]:
        """Get all compatibility entries for a platform version."""
        return sorted(
            [e for e in self._entries.values() if e.platform_version == platform_version],
            key=lambda e: (e.app_id, e.app_version),
        )
