"""Sandbox API Version — manage versioned API endpoints for extensions.

Supports multiple API versions simultaneously with routing, deprecation
notices, migration guides, and version negotiation.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


class VersionStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    SUNSET = "sunset"
    BETA = "beta"


@dataclass
class ApiVersion:
    version: str  # e.g. "v1", "v2"
    status: VersionStatus = VersionStatus.ACTIVE
    endpoints: list[str] = field(default_factory=list)
    sunset_date: str = ""
    migration_guide: str = ""
    request_count: int = 0


class SandboxApiVersionService:
    """Manages versioned API endpoints with deprecation."""

    def __init__(self):
        self._versions: dict[str, dict[str, ApiVersion]] = defaultdict(dict)
        self._default: dict[str, str] = {}

    def register_version(self, sandbox_id: str, version: str,
                         endpoints: list[str],
                         status: VersionStatus = VersionStatus.ACTIVE) -> ApiVersion:
        av = ApiVersion(version=version, status=status, endpoints=endpoints)
        self._versions[sandbox_id][version] = av
        if status == VersionStatus.ACTIVE and sandbox_id not in self._default:
            self._default[sandbox_id] = version
        return av

    def set_default(self, sandbox_id: str, version: str) -> bool:
        if version in self._versions.get(sandbox_id, {}):
            self._default[sandbox_id] = version
            return True
        return False

    def deprecate(self, sandbox_id: str, version: str,
                  sunset_date: str = "", migration_guide: str = "") -> bool:
        av = self._versions.get(sandbox_id, {}).get(version)
        if not av:
            return False
        av.status = VersionStatus.DEPRECATED
        av.sunset_date = sunset_date
        av.migration_guide = migration_guide
        return True

    def resolve(self, sandbox_id: str, requested_version: str | None = None) -> dict:
        versions = self._versions.get(sandbox_id, {})
        if not versions:
            return {"resolved": False, "error": "No versions registered"}

        version = requested_version or self._default.get(sandbox_id, "")
        av = versions.get(version)
        if not av:
            return {"resolved": False, "error": f"Version '{version}' not found"}

        av.request_count += 1
        warnings = []
        if av.status == VersionStatus.DEPRECATED:
            warnings.append(f"Version {version} is deprecated")
            if av.sunset_date:
                warnings.append(f"Sunset: {av.sunset_date}")
        if av.status == VersionStatus.SUNSET:
            return {"resolved": False, "error": f"Version {version} has been sunset"}

        return {
            "resolved": True, "version": version,
            "status": av.status.value, "endpoints": av.endpoints,
            "warnings": warnings,
        }

    def list_versions(self, sandbox_id: str) -> list[dict]:
        return [
            {"version": av.version, "status": av.status.value,
             "endpoints": len(av.endpoints), "requests": av.request_count,
             "is_default": av.version == self._default.get(sandbox_id)}
            for av in self._versions.get(sandbox_id, {}).values()
        ]

    def get_migration_path(self, sandbox_id: str, from_v: str, to_v: str) -> dict:
        versions = self._versions.get(sandbox_id, {})
        from_av = versions.get(from_v)
        to_av = versions.get(to_v)
        if not from_av or not to_av:
            return {"error": "Version not found"}
        added = [e for e in to_av.endpoints if e not in from_av.endpoints]
        removed = [e for e in from_av.endpoints if e not in to_av.endpoints]
        return {"from": from_v, "to": to_v, "added": added,
                "removed": removed, "guide": to_av.migration_guide}
