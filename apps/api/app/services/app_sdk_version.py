"""App SDK Version — track SDK versions used by consumers.

Manages SDK version tracking:
- Record SDK versions from API requests
- Track adoption rates per version
- Identify outdated consumers
- Per-installation scoped tracking
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class SDKVersionInfo:
    """SDK version usage info."""

    version: str
    request_count: int = 0
    unique_consumers: set[str] = field(default_factory=set)
    latest: bool = False

    @property
    def consumer_count(self) -> int:
        return len(self.unique_consumers)


class AppSDKVersion:
    """Track SDK versions used by consumers."""

    def __init__(self) -> None:
        self._versions: dict[tuple[str, str], SDKVersionInfo] = {}
        self._latest: dict[str, str] = {}

    def set_latest(self, installation_id: str, version: str) -> None:
        if not installation_id:
            raise ValueError("installation_id is required")
        self._latest[installation_id] = version
        # Update flags
        for (inst, v), info in self._versions.items():
            if inst == installation_id:
                info.latest = (v == version)

    def record_usage(
        self, installation_id: str, version: str, consumer_id: str,
    ) -> SDKVersionInfo:
        if not installation_id:
            raise ValueError("installation_id is required")

        key = (installation_id, version)
        if key not in self._versions:
            latest_ver = self._latest.get(installation_id, "")
            self._versions[key] = SDKVersionInfo(version=version, latest=(version == latest_ver))

        info = self._versions[key]
        info.request_count += 1
        info.unique_consumers.add(consumer_id)
        return info

    def outdated_consumers(self, installation_id: str) -> list[dict]:
        """Consumers using non-latest versions."""
        latest = self._latest.get(installation_id)
        if not latest:
            return []
        result: dict[str, str] = {}
        for (inst, ver), info in self._versions.items():
            if inst == installation_id and ver != latest:
                for c in info.unique_consumers:
                    result[c] = ver
        return [{"consumer": c, "version": v} for c, v in sorted(result.items())]

    def version_stats(self, installation_id: str) -> list[dict]:
        stats = []
        for (inst, _), info in self._versions.items():
            if inst == installation_id:
                stats.append({
                    "version": info.version, "requests": info.request_count,
                    "consumers": info.consumer_count, "latest": info.latest,
                })
        return sorted(stats, key=lambda x: x["version"], reverse=True)

    def list_versions(self, installation_id: str) -> list[str]:
        return sorted(
            [v for (inst, v) in self._versions if inst == installation_id],
            reverse=True,
        )
