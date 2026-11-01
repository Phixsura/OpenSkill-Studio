"""App API Versioning — manage API version lifecycle.

Manages API versions:
- Register versions with status
- Track active/deprecated/sunset versions
- Version migration paths
- Per-installation scoped versions
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class VersionStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    SUNSET = "sunset"


@dataclass
class APIVersion:
    """An API version."""

    version: str
    status: VersionStatus = VersionStatus.DRAFT
    endpoint_count: int = 0
    migration_from: str | None = None  # previous version


class AppAPIVersioning:
    """Manage API version lifecycle."""

    def __init__(self) -> None:
        self._versions: dict[tuple[str, str], APIVersion] = {}

    def register(
        self, installation_id: str, version: str,
        endpoint_count: int = 0, migration_from: str | None = None,
    ) -> APIVersion:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not version:
            raise ValueError("version is required")

        key = (installation_id, version)
        if key in self._versions:
            raise ValueError(f"Version {version} already registered")

        v = APIVersion(
            version=version, endpoint_count=endpoint_count,
            migration_from=migration_from,
        )
        self._versions[key] = v
        return v

    def activate(self, installation_id: str, version: str) -> APIVersion:
        v = self._get(installation_id, version)
        if v.status != VersionStatus.DRAFT:
            raise ValueError("Only draft versions can be activated")
        v.status = VersionStatus.ACTIVE
        return v

    def deprecate(self, installation_id: str, version: str) -> APIVersion:
        v = self._get(installation_id, version)
        v.status = VersionStatus.DEPRECATED
        return v

    def sunset(self, installation_id: str, version: str) -> APIVersion:
        v = self._get(installation_id, version)
        v.status = VersionStatus.SUNSET
        return v

    def active_versions(self, installation_id: str) -> list[APIVersion]:
        return [v for (inst, _), v in self._versions.items() if inst == installation_id and v.status == VersionStatus.ACTIVE]

    def list_versions(self, installation_id: str) -> list[APIVersion]:
        return [v for (inst, _), v in self._versions.items() if inst == installation_id]

    def _get(self, installation_id: str, version: str) -> APIVersion:
        key = (installation_id, version)
        v = self._versions.get(key)
        if v is None:
            raise KeyError(f"Version {version} not found")
        return v
