"""API Versioning Manager — semantic versioning with deprecation tracking."""
from __future__ import annotations

import re
import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = structlog.get_logger()

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def parse_semver(version: str) -> tuple[int, int, int]:
    m = SEMVER_RE.match(version)
    if not m:
        raise ValueError(f"Invalid semver: {version}")
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


@dataclass
class ApiVersion:
    version: str
    status: str = "active"  # active, deprecated, sunset
    release_date: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    deprecation_date: str | None = None
    sunset_date: str | None = None
    changelog: str = ""


@dataclass
class VersioningManager:
    """Manage API versions with deprecation lifecycle."""

    _versions: dict[str, ApiVersion] = field(default_factory=dict)

    def register(self, version: str, changelog: str = "") -> dict:
        parse_semver(version)  # validate
        if version in self._versions:
            raise ValueError(f"Version {version} already registered")
        self._versions[version] = ApiVersion(version=version, changelog=changelog)
        logger.info("version_registered", version=version)
        return {"version": version, "status": "active"}

    def deprecate(self, version: str, sunset_date: str | None = None) -> dict:
        v = self._versions.get(version)
        if not v:
            raise ValueError(f"Version {version} not found")
        if v.status == "sunset":
            raise ValueError(f"Version {version} already sunset")
        v.status = "deprecated"
        v.deprecation_date = datetime.now(timezone.utc).isoformat()
        v.sunset_date = sunset_date
        logger.info("version_deprecated", version=version)
        return {"version": version, "status": "deprecated", "sunset_date": sunset_date}

    def sunset(self, version: str) -> dict:
        v = self._versions.get(version)
        if not v:
            raise ValueError(f"Version {version} not found")
        v.status = "sunset"
        v.sunset_date = datetime.now(timezone.utc).isoformat()
        logger.info("version_sunset", version=version)
        return {"version": version, "status": "sunset"}

    def get_latest(self) -> dict | None:
        active = [v for v in self._versions.values() if v.status == "active"]
        if not active:
            return None
        latest = max(active, key=lambda v: parse_semver(v.version))
        return {"version": latest.version, "status": latest.status,
                "release_date": latest.release_date}

    def list_versions(self, status: str | None = None) -> list[dict]:
        versions = list(self._versions.values())
        if status:
            versions = [v for v in versions if v.status == status]
        versions.sort(key=lambda v: parse_semver(v.version), reverse=True)
        return [
            {"version": v.version, "status": v.status, "release_date": v.release_date,
             "deprecation_date": v.deprecation_date, "sunset_date": v.sunset_date}
            for v in versions
        ]

    def check_compatibility(self, from_version: str, to_version: str) -> dict:
        f = parse_semver(from_version)
        t = parse_semver(to_version)
        if f[0] != t[0]:
            breaking = True
            level = "major"
        elif f[1] != t[1]:
            breaking = False
            level = "minor"
        else:
            breaking = False
            level = "patch"
        return {
            "from": from_version,
            "to": to_version,
            "level": level,
            "breaking": breaking,
            "upgrade_path": "direct" if not breaking else "migration_required",
        }

    def get_migration_path(self, from_version: str, to_version: str) -> list[str]:
        f = parse_semver(from_version)
        t = parse_semver(to_version)
        if f >= t:
            return []
        sorted_versions = sorted(self._versions.keys(), key=parse_semver)
        path = [v for v in sorted_versions if f < parse_semver(v) <= t]
        return path
