"""SDK Version Manager — manage SDK versions with compatibility matrix.

Tracks SDK releases, maps SDK→platform compatibility, handles deprecation
notices, and recommends upgrade paths for extension developers.
"""
from __future__ import annotations
import re
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


class SDKStatus(str, Enum):
    STABLE = "stable"
    BETA = "beta"
    DEPRECATED = "deprecated"
    EOL = "end_of_life"


SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def _parse_semver(v: str) -> tuple[int, int, int]:
    m = SEMVER_RE.match(v)
    if not m:
        raise ValueError(f"Invalid semver: {v}")
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


@dataclass
class SDKRelease:
    version: str
    status: SDKStatus
    min_platform_version: str
    max_platform_version: str
    changelog: str = ""
    deprecation_message: str = ""
    release_date: str = ""


@dataclass
class UpgradePath:
    from_version: str
    to_version: str
    steps: list[str]
    has_breaking_changes: bool
    migration_guide_url: str = ""


class SDKVersionManagerService:
    """Manages SDK versions with compatibility and upgrade paths."""

    def __init__(self):
        self._releases: dict[str, SDKRelease] = {}
        self._upgrade_paths: list[UpgradePath] = []

    def register_release(self, version: str, status: SDKStatus,
                         min_platform: str, max_platform: str,
                         changelog: str = "", release_date: str = "") -> SDKRelease:
        _parse_semver(version)  # validate
        release = SDKRelease(
            version=version, status=status,
            min_platform_version=min_platform,
            max_platform_version=max_platform,
            changelog=changelog, release_date=release_date,
        )
        self._releases[version] = release
        return release

    def deprecate(self, version: str, message: str) -> bool:
        release = self._releases.get(version)
        if not release:
            return False
        release.status = SDKStatus.DEPRECATED
        release.deprecation_message = message
        return True

    def check_compatibility(self, sdk_version: str, platform_version: str) -> dict:
        release = self._releases.get(sdk_version)
        if not release:
            return {"compatible": False, "reason": "SDK version not found"}

        sdk_min = _parse_semver(release.min_platform_version)
        sdk_max = _parse_semver(release.max_platform_version)
        plat = _parse_semver(platform_version)

        if plat < sdk_min:
            return {"compatible": False, "reason": f"Platform too old (min {release.min_platform_version})"}
        if plat > sdk_max:
            return {"compatible": False, "reason": f"Platform too new (max {release.max_platform_version})"}
        if release.status == SDKStatus.EOL:
            return {"compatible": False, "reason": "SDK version is end-of-life"}

        warnings = []
        if release.status == SDKStatus.DEPRECATED:
            warnings.append(release.deprecation_message or "This SDK version is deprecated")
        if release.status == SDKStatus.BETA:
            warnings.append("This is a beta SDK version")

        return {"compatible": True, "warnings": warnings}

    def add_upgrade_path(self, from_v: str, to_v: str, steps: list[str],
                         has_breaking: bool = False, guide_url: str = "") -> UpgradePath:
        path = UpgradePath(
            from_version=from_v, to_version=to_v, steps=steps,
            has_breaking_changes=has_breaking, migration_guide_url=guide_url,
        )
        self._upgrade_paths.append(path)
        return path

    def get_upgrade_path(self, from_v: str, to_v: str) -> UpgradePath | None:
        return next((p for p in self._upgrade_paths
                     if p.from_version == from_v and p.to_version == to_v), None)

    def recommend_version(self, platform_version: str) -> str | None:
        compatible = []
        for v, r in self._releases.items():
            if r.status in (SDKStatus.STABLE, SDKStatus.BETA):
                result = self.check_compatibility(v, platform_version)
                if result["compatible"]:
                    compatible.append((v, r))
        # Prefer stable, then latest
        stable = [(v, r) for v, r in compatible if r.status == SDKStatus.STABLE]
        if stable:
            return max(stable, key=lambda x: _parse_semver(x[0]))[0]
        if compatible:
            return max(compatible, key=lambda x: _parse_semver(x[0]))[0]
        return None

    def list_releases(self, status: SDKStatus | None = None) -> list[SDKRelease]:
        releases = list(self._releases.values())
        if status:
            releases = [r for r in releases if r.status == status]
        releases.sort(key=lambda r: _parse_semver(r.version), reverse=True)
        return releases
