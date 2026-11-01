"""API Version Strategy — multi-strategy version negotiation.

Implements:
- URL path versioning (/v1/, /v2/)
- Header versioning (Accept: application/vnd.api.v2+json)
- Query param versioning (?version=2)
- Version lifecycle: active, deprecated, sunset
- Automatic version routing to correct handler
- Migration guides between versions
"""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import time


@dataclass
class ApiVersionDef:
    version: str  # "v1", "v2"
    status: str = "active"  # active, deprecated, sunset
    released_at: float = 0.0
    deprecated_at: float = 0.0
    sunset_at: float = 0.0
    handlers: dict[str, callable] = field(default_factory=dict)  # endpoint → handler
    changelog: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.released_at: self.released_at = time.time()


HEADER_RE = re.compile(r'application/vnd\.(\w+)\.v(\d+)\+json')


class ApiVersionStrategyService:
    def __init__(self, default_version: str = "v1"):
        self._versions: dict[str, ApiVersionDef] = {}
        self._default = default_version
        self._migration_guides: dict[str, str] = {}  # "v1→v2" → guide text

    def register_version(self, version: str, status: str = "active",
                         changelog: list[str] | None = None) -> ApiVersionDef:
        v = ApiVersionDef(version=version, status=status,
                          changelog=changelog or [])
        self._versions[version] = v
        return v

    def register_handler(self, version: str, endpoint: str,
                         handler: callable) -> bool:
        v = self._versions.get(version)
        if not v: return False
        v.handlers[endpoint] = handler
        return True

    def deprecate(self, version: str, sunset_days: int = 90) -> bool:
        v = self._versions.get(version)
        if not v or v.status != "active": return False
        now = time.time()
        v.status = "deprecated"
        v.deprecated_at = now
        v.sunset_at = now + sunset_days * 86400
        return True

    def sunset(self, version: str) -> bool:
        v = self._versions.get(version)
        if not v: return False
        v.status = "sunset"
        v.sunset_at = time.time()
        return True

    def negotiate(self, path: str = "", accept_header: str = "",
                  query_version: str = "") -> dict:
        """Determine API version from request. Returns version info."""
        version = None
        source = ""

        # 1. URL path (/v2/users)
        path_match = re.match(r'^/v(\d+)/', path)
        if path_match:
            version = f"v{path_match.group(1)}"
            source = "path"

        # 2. Accept header
        if not version and accept_header:
            header_match = HEADER_RE.search(accept_header)
            if header_match:
                version = f"v{header_match.group(2)}"
                source = "header"

        # 3. Query parameter
        if not version and query_version:
            version = query_version if query_version.startswith("v") else f"v{query_version}"
            source = "query"

        # 4. Default
        if not version:
            version = self._default
            source = "default"

        v = self._versions.get(version)
        if not v:
            return {"version": version, "status": "not_found", "source": source}

        result = {"version": version, "status": v.status, "source": source}

        if v.status == "deprecated":
            result["warning"] = f"API {version} is deprecated. Migrate to latest."
            result["sunset_at"] = v.sunset_at
        elif v.status == "sunset":
            result["error"] = f"API {version} has been sunset. Use latest version."

        return result

    def route(self, version: str, endpoint: str) -> callable | None:
        """Get handler for version + endpoint."""
        v = self._versions.get(version)
        if not v or v.status == "sunset":
            return None
        return v.handlers.get(endpoint)

    def add_migration_guide(self, from_v: str, to_v: str, guide: str) -> None:
        self._migration_guides[f"{from_v}→{to_v}"] = guide

    def get_migration_guide(self, from_v: str, to_v: str) -> str:
        return self._migration_guides.get(f"{from_v}→{to_v}", "")

    def list_versions(self) -> list[dict]:
        return [{"version": v.version, "status": v.status,
                 "endpoints": len(v.handlers)}
                for v in sorted(self._versions.values(),
                                key=lambda x: x.version, reverse=True)]
