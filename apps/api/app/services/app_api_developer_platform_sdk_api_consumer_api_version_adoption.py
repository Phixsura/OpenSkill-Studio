"""App API Developer Consumer API Version Adoption — track which API versions consumers use."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class VersionAdoption:
    consumer_id: str
    versions_used: dict[str, int] = field(default_factory=dict)  # version -> request count

    @property
    def primary_version(self) -> str:
        if not self.versions_used: return ""
        return max(self.versions_used, key=self.versions_used.get)

    @property
    def using_latest(self) -> bool:
        return self.primary_version.startswith("v2") if self.primary_version else False

    @property
    def multi_version(self) -> bool:
        return len(self.versions_used) > 1

class AppAPIDeveloperPlatformSDKApiConsumerApiVersionAdoption:
    def __init__(self) -> None:
        self._adoptions: dict[tuple[str, str], VersionAdoption] = {}

    def record(self, installation_id: str, consumer_id: str, version: str, count: int = 1) -> VersionAdoption:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, consumer_id)
        if key not in self._adoptions:
            self._adoptions[key] = VersionAdoption(consumer_id=consumer_id)
        a = self._adoptions[key]
        a.versions_used[version] = a.versions_used.get(version, 0) + count
        return a

    def on_old_versions(self, installation_id: str, latest_prefix: str = "v2") -> list[VersionAdoption]:
        return [a for (inst, _), a in self._adoptions.items() if inst == installation_id and not a.primary_version.startswith(latest_prefix)]

    def version_distribution(self, installation_id: str) -> dict[str, int]:
        dist: dict[str, int] = {}
        for (inst, _), a in self._adoptions.items():
            if inst == installation_id:
                for v, c in a.versions_used.items():
                    dist[v] = dist.get(v, 0) + c
        return dist

    def all_adoptions(self, installation_id: str) -> list[VersionAdoption]:
        return [a for (inst, _), a in self._adoptions.items() if inst == installation_id]
