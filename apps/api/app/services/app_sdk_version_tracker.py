"""App SDK Version Tracker — track SDK versions used by app installations.

Manages SDK version tracking:
- Record SDK version per installation
- Detect outdated installations
- Version distribution stats
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()

_SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)")


def _parse_ver(v: str) -> tuple[int, int, int]:
    m = _SEMVER_RE.match(v)
    if not m:
        return (0, 0, 0)
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


@dataclass
class SDKUsage:
    """SDK usage record."""

    installation_id: str
    sdk_version: str
    language: str  # python, typescript, etc.
    last_seen: float = 0.0


class AppSDKVersionTracker:
    """Track SDK versions used by installations."""

    def __init__(self, latest_version: str = "0.0.0") -> None:
        self._latest = latest_version
        self._usage: dict[str, SDKUsage] = {}

    def record(
        self,
        installation_id: str,
        sdk_version: str,
        language: str = "unknown",
        now: float = 0.0,
    ) -> SDKUsage:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not sdk_version:
            raise ValueError("sdk_version is required")

        usage = SDKUsage(
            installation_id=installation_id,
            sdk_version=sdk_version, language=language, last_seen=now,
        )
        self._usage[installation_id] = usage
        return usage

    def is_outdated(self, installation_id: str) -> bool:
        usage = self._usage.get(installation_id)
        if usage is None:
            return False
        return _parse_ver(usage.sdk_version) < _parse_ver(self._latest)

    def get_outdated(self) -> list[SDKUsage]:
        latest = _parse_ver(self._latest)
        return [u for u in self._usage.values() if _parse_ver(u.sdk_version) < latest]

    def version_distribution(self) -> dict[str, int]:
        dist: dict[str, int] = {}
        for u in self._usage.values():
            dist[u.sdk_version] = dist.get(u.sdk_version, 0) + 1
        return dist

    def language_distribution(self) -> dict[str, int]:
        dist: dict[str, int] = {}
        for u in self._usage.values():
            dist[u.language] = dist.get(u.language, 0) + 1
        return dist

    def get_usage(self, installation_id: str) -> SDKUsage | None:
        return self._usage.get(installation_id)

    def set_latest(self, version: str) -> None:
        self._latest = version

    def total_installations(self) -> int:
        return len(self._usage)
