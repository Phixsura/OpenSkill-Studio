"""API Versioning — manage multiple API versions for backward compatibility.

Supports URL-based versioning (v1, v2), version negotiation,
deprecation notices, and sunset scheduling for old API versions.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class VersionStatus(str, Enum):
    CURRENT = "current"
    SUPPORTED = "supported"
    DEPRECATED = "deprecated"
    SUNSET = "sunset"


@dataclass
class APIVersion:
    version: str  # "v1", "v2"
    status: VersionStatus
    released_at: str
    deprecated_at: str = ""
    sunset_at: str = ""
    changelog: str = ""
    breaking_changes: list[str] = field(default_factory=list)


class APIVersionManager:
    """Manages API version lifecycle and negotiation."""

    def __init__(self):
        self._versions: dict[str, APIVersion] = {}
        self._current: str = ""

    def register_version(self, version: str, status: VersionStatus,
                         released_at: str, changelog: str = "",
                         breaking_changes: list[str] | None = None) -> APIVersion:
        v = APIVersion(
            version=version, status=status, released_at=released_at,
            changelog=changelog, breaking_changes=breaking_changes or [],
        )
        self._versions[version] = v
        if status == VersionStatus.CURRENT:
            self._current = version
        return v

    def get_current(self) -> str:
        return self._current

    def get_version(self, version: str) -> APIVersion | None:
        return self._versions.get(version)

    def deprecate(self, version: str, sunset_at: str = "") -> bool:
        v = self._versions.get(version)
        if not v:
            return False
        v.status = VersionStatus.DEPRECATED
        v.deprecated_at = datetime.now(timezone.utc).isoformat()
        v.sunset_at = sunset_at
        return True

    def sunset(self, version: str) -> bool:
        v = self._versions.get(version)
        if not v:
            return False
        v.status = VersionStatus.SUNSET
        return True

    def negotiate(self, requested: str) -> tuple[str, dict]:
        """Negotiate API version. Returns (version, headers)."""
        headers: dict[str, str] = {}

        if requested in self._versions:
            v = self._versions[requested]
            if v.status == VersionStatus.SUNSET:
                return self._current, {
                    "X-API-Version": self._current,
                    "X-Sunset-Notice": f"Version {requested} has been sunset. Using {self._current}.",
                }
            if v.status == VersionStatus.DEPRECATED:
                headers["X-API-Version"] = requested
                headers["X-Deprecation-Notice"] = f"Version {requested} is deprecated."
                if v.sunset_at:
                    headers["X-Sunset-Date"] = v.sunset_at
                return requested, headers
            return requested, {"X-API-Version": requested}

        return self._current, {
            "X-API-Version": self._current,
            "X-Fallback": f"Unknown version {requested}. Using {self._current}.",
        }

    def list_versions(self, include_sunset: bool = False) -> list[APIVersion]:
        versions = list(self._versions.values())
        if not include_sunset:
            versions = [v for v in versions if v.status != VersionStatus.SUNSET]
        return sorted(versions, key=lambda v: v.version, reverse=True)

    def get_migration_guide(self, from_ver: str, to_ver: str) -> dict:
        """Get breaking changes between two versions."""
        changes = []
        versions = sorted(self._versions.keys())
        collecting = False
        for v in versions:
            if v == from_ver:
                collecting = True
                continue
            if collecting:
                ver = self._versions[v]
                changes.extend(ver.breaking_changes)
                if v == to_ver:
                    break
        return {"from": from_ver, "to": to_ver, "breaking_changes": changes}
