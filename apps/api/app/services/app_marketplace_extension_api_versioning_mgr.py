"""API Versioning Manager — manage multiple API versions with deprecation."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class ApiVersion:
    version: str  # e.g. "v1", "v2"
    status: str = "active"  # active, deprecated, sunset
    released_at: float = 0.0
    deprecated_at: float = 0.0
    sunset_at: float = 0.0
    changelog: list[str] = field(default_factory=list)
    def __post_init__(self):
        if not self.released_at: self.released_at = time.time()


class ApiVersioningMgrService:
    def __init__(self):
        self._versions: dict[str, ApiVersion] = {}

    def register(self, version: str, changelog: list[str] | None = None) -> ApiVersion:
        v = ApiVersion(version=version, changelog=changelog or [])
        self._versions[version] = v
        return v

    def deprecate(self, version: str, sunset_days: int = 90) -> bool:
        v = self._versions.get(version)
        if not v or v.status != "active":
            return False
        v.status = "deprecated"
        v.deprecated_at = time.time()
        v.sunset_at = v.deprecated_at + sunset_days * 86400
        return True

    def sunset(self, version: str) -> bool:
        v = self._versions.get(version)
        if not v:
            return False
        v.status = "sunset"
        v.sunset_at = time.time()
        return True

    def get_active(self) -> list[ApiVersion]:
        return [v for v in self._versions.values() if v.status == "active"]

    def get_latest(self) -> ApiVersion | None:
        active = self.get_active()
        return max(active, key=lambda v: v.released_at) if active else None

    def is_supported(self, version: str) -> bool:
        v = self._versions.get(version)
        return v is not None and v.status != "sunset"

    def get_all(self) -> list[ApiVersion]:
        return sorted(self._versions.values(), key=lambda v: v.released_at, reverse=True)
