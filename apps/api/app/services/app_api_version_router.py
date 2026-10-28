"""App API Version Router — route requests to correct API versions.

Manages API versioning for installed apps:
- Register API versions with status (active, deprecated, sunset)
- Resolve version from request headers
- Default version fallback
- Per-installation scoped versioning
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import structlog

log = structlog.get_logger()


class VersionStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    SUNSET = "sunset"


@dataclass
class APIVersion:
    """An API version."""

    version: str
    status: VersionStatus
    base_path: str  # e.g. "/api/v2"
    sunset_date: str = ""


class AppAPIVersionRouter:
    """Route requests to correct API versions."""

    def __init__(self) -> None:
        # (installation_id, version) → APIVersion
        self._versions: dict[tuple[str, str], APIVersion] = {}
        # installation_id → default version
        self._defaults: dict[str, str] = {}

    def register_version(
        self,
        installation_id: str,
        version: str,
        base_path: str,
        status: VersionStatus = VersionStatus.ACTIVE,
        sunset_date: str = "",
    ) -> APIVersion:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not version:
            raise ValueError("version is required")
        if not base_path:
            raise ValueError("base_path is required")

        key = (installation_id, version)
        if key in self._versions:
            raise ValueError(f"Version {version} already registered")

        api_ver = APIVersion(
            version=version, status=status,
            base_path=base_path, sunset_date=sunset_date,
        )
        self._versions[key] = api_ver
        return api_ver

    def set_default(self, installation_id: str, version: str) -> None:
        key = (installation_id, version)
        if key not in self._versions:
            raise KeyError(f"Version {version} not registered")
        self._defaults[installation_id] = version

    def resolve(
        self, installation_id: str, requested_version: str | None = None
    ) -> APIVersion:
        """Resolve which version to use."""
        version = requested_version or self._defaults.get(installation_id)
        if version is None:
            raise ValueError("No version specified and no default set")

        key = (installation_id, version)
        api_ver = self._versions.get(key)
        if api_ver is None:
            raise KeyError(f"Version {version} not found")

        if api_ver.status == VersionStatus.SUNSET:
            raise ValueError(f"Version {version} has been sunset")

        return api_ver

    def list_versions(self, installation_id: str) -> list[APIVersion]:
        return [v for (inst, _), v in self._versions.items() if inst == installation_id]

    def get_active_versions(self, installation_id: str) -> list[APIVersion]:
        return [
            v for (inst, _), v in self._versions.items()
            if inst == installation_id and v.status == VersionStatus.ACTIVE
        ]
