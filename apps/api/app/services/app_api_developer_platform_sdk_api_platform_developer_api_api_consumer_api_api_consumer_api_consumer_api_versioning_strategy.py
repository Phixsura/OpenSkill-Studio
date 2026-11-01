"""Consumer API Versioning Strategy — manage API version routing and compatibility."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class APIVersion:
    version: str          # "v1", "v2", "2024-01-01"
    status: str = "active"  # "active", "deprecated", "sunset"
    released_at: datetime | None = None
    sunset_at: datetime | None = None
    changelog: str = ""

@dataclass
class VersionStrategy:
    strategy_type: str = "path"  # "path" (/v1/), "header" (X-API-Version), "query" (?version=)
    default_version: str = "v1"
    header_name: str = "X-API-Version"
    allow_version_override: bool = True

@dataclass
class VersionResolution:
    resolved_version: str
    source: str  # "path", "header", "query", "default", "pinned"
    deprecated: bool = False

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiVersioningStrategy:
    def __init__(self) -> None:
        self._versions: dict[tuple[str, str], APIVersion] = {}
        self._strategies: dict[str, VersionStrategy] = {}
        self._pins: dict[tuple[str, str], str] = {}  # (inst, consumer) -> version

    def register_version(self, installation_id: str, version: APIVersion) -> APIVersion:
        if not installation_id:
            raise ValueError("installation_id is required")
        if version.status not in ("active", "deprecated", "sunset"):
            raise ValueError(f"Invalid status: {version.status}")
        self._versions[(installation_id, version.version)] = version
        return version

    def set_strategy(self, installation_id: str, strategy: VersionStrategy) -> VersionStrategy:
        if strategy.strategy_type not in ("path", "header", "query"):
            raise ValueError(f"Invalid strategy: {strategy.strategy_type}")
        self._strategies[installation_id] = strategy
        return strategy

    def pin_consumer(self, installation_id: str, consumer_id: str, version: str) -> None:
        if (installation_id, version) not in self._versions:
            raise ValueError(f"Version {version} not registered")
        self._pins[(installation_id, consumer_id)] = version

    def resolve(self, installation_id: str, consumer_id: str, path_version: str | None = None, header_version: str | None = None, query_version: str | None = None) -> VersionResolution:
        strategy = self._strategies.get(installation_id, VersionStrategy())
        # Check pin first
        pinned = self._pins.get((installation_id, consumer_id))
        if pinned:
            v = self._versions.get((installation_id, pinned))
            return VersionResolution(resolved_version=pinned, source="pinned", deprecated=v.status == "deprecated" if v else False)
        # Resolve by strategy
        resolved = None
        source = "default"
        if strategy.allow_version_override:
            if strategy.strategy_type == "path" and path_version:
                resolved, source = path_version, "path"
            elif strategy.strategy_type == "header" and header_version:
                resolved, source = header_version, "header"
            elif strategy.strategy_type == "query" and query_version:
                resolved, source = query_version, "query"
        if not resolved:
            resolved = strategy.default_version
        v = self._versions.get((installation_id, resolved))
        return VersionResolution(resolved_version=resolved, source=source, deprecated=v.status == "deprecated" if v else False)

    def list_versions(self, installation_id: str) -> list[APIVersion]:
        return sorted([v for (inst, _), v in self._versions.items() if inst == installation_id], key=lambda v: v.version)
