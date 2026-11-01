"""API Version Negotiator — negotiate API version from request headers/params."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import structlog

log = structlog.get_logger()

@dataclass
class VersionConfig:
    version: str
    status: str = "stable"  # "stable", "beta", "deprecated", "sunset"
    supported: bool = True

_VERSION_RE = re.compile(r"^v\d+(\.\d+)?$")

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiVersionNegotiator:
    def __init__(self) -> None:
        self._versions: dict[tuple[str, str], VersionConfig] = {}
        self._defaults: dict[str, str] = {}

    def register_version(self, installation_id: str, version: str, status: str = "stable") -> VersionConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if not _VERSION_RE.match(version): raise ValueError(f"Invalid version format: {version} (expected vN or vN.N)")
        valid_statuses = {"stable", "beta", "deprecated", "sunset"}
        if status not in valid_statuses: raise ValueError(f"Invalid status: {status}")
        vc = VersionConfig(version=version, status=status, supported=status != "sunset")
        self._versions[(installation_id, version)] = vc
        return vc

    def set_default(self, installation_id: str, version: str) -> None:
        if (installation_id, version) not in self._versions: raise KeyError(f"Version {version} not registered")
        self._defaults[installation_id] = version

    def negotiate(self, installation_id: str, requested: str | None = None, accept_header: str = "") -> VersionConfig:
        # 1. Explicit version parameter
        if requested:
            vc = self._versions.get((installation_id, requested))
            if vc and vc.supported: return vc
            if vc and not vc.supported: raise ValueError(f"Version {requested} is sunset")
        # 2. Accept header: application/vnd.api.vN+json
        if accept_header:
            m = re.search(r"vnd\.api\.(v[\d.]+)\+json", accept_header)
            if m:
                vc = self._versions.get((installation_id, m.group(1)))
                if vc and vc.supported: return vc
        # 3. Default
        default_ver = self._defaults.get(installation_id)
        if default_ver:
            vc = self._versions.get((installation_id, default_ver))
            if vc: return vc
        # 4. Latest stable
        stables = [(v, vc) for (inst, v), vc in self._versions.items() if inst == installation_id and vc.status == "stable"]
        if stables: return sorted(stables, key=lambda x: x[0])[-1][1]
        raise KeyError("No supported version available")

    def list_versions(self, installation_id: str) -> list[VersionConfig]:
        return [vc for (inst, _), vc in self._versions.items() if inst == installation_id]

    def deprecated_versions(self, installation_id: str) -> list[VersionConfig]:
        return [vc for (inst, _), vc in self._versions.items() if inst == installation_id and vc.status in ("deprecated", "sunset")]
