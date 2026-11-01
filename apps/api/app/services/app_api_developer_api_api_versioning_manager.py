"""App API Developer API Versioning Manager — manage API version lifecycle."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class APIVersion:
    version: str
    status: str  # "active", "deprecated", "sunset"
    created_at: float = field(default_factory=time.time)
    deprecated_at: float | None = None
    sunset_at: float | None = None
    endpoints_count: int = 0
    traffic_pct: float = 0.0

class AppAPIDeveloperAPIApiVersioningManager:
    def __init__(self) -> None:
        self._versions: dict[tuple[str, str], APIVersion] = {}

    def register(self, installation_id: str, version: str, endpoints_count: int = 0) -> APIVersion:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, version)
        if key in self._versions: raise ValueError(f"Version {version} already exists")
        v = APIVersion(version=version, status="active", endpoints_count=endpoints_count)
        self._versions[key] = v
        return v

    def deprecate(self, installation_id: str, version: str, sunset_at: float) -> APIVersion:
        v = self._get(installation_id, version)
        if v.status == "sunset": raise ValueError("Cannot deprecate a sunset version")
        v.status = "deprecated"
        v.deprecated_at = time.time()
        v.sunset_at = sunset_at
        return v

    def sunset(self, installation_id: str, version: str) -> APIVersion:
        v = self._get(installation_id, version)
        v.status = "sunset"
        return v

    def update_traffic(self, installation_id: str, version: str, traffic_pct: float) -> APIVersion:
        v = self._get(installation_id, version)
        v.traffic_pct = traffic_pct
        return v

    def list_versions(self, installation_id: str) -> list[APIVersion]:
        return [v for (inst, _), v in self._versions.items() if inst == installation_id]

    def active_versions(self, installation_id: str) -> list[APIVersion]:
        return [v for (inst, _), v in self._versions.items() if inst == installation_id and v.status == "active"]

    def _get(self, installation_id: str, version: str) -> APIVersion:
        key = (installation_id, version)
        v = self._versions.get(key)
        if v is None: raise KeyError(f"Version {version} not found")
        return v
