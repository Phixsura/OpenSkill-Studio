"""API Consumer Endpoint Versioning — manage multiple API versions per endpoint."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class EndpointVersion:
    version: str
    status: str = "active"  # "active", "deprecated", "sunset"
    handler: str = ""  # handler reference
    consumers_using: int = 0

@dataclass
class VersionedEndpoint:
    endpoint: str
    method: str
    versions: list[EndpointVersion] = field(default_factory=list)
    default_version: str = ""

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointVersioning:
    def __init__(self) -> None:
        self._endpoints: dict[tuple[str, str, str], VersionedEndpoint] = {}

    def register(self, installation_id: str, endpoint: str, method: str, version: str, handler: str = "") -> VersionedEndpoint:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, method.upper(), endpoint)
        ve = self._endpoints.get(key)
        if ve is None:
            ve = VersionedEndpoint(endpoint=endpoint, method=method.upper())
            self._endpoints[key] = ve
        if any(v.version == version for v in ve.versions):
            raise ValueError(f"Version {version} already registered")
        ve.versions.append(EndpointVersion(version=version, handler=handler))
        if not ve.default_version: ve.default_version = version
        return ve

    def resolve(self, installation_id: str, endpoint: str, method: str, requested_version: str = "") -> EndpointVersion | None:
        ve = self._endpoints.get((installation_id, method.upper(), endpoint))
        if ve is None: return None
        if requested_version:
            return next((v for v in ve.versions if v.version == requested_version and v.status != "sunset"), None)
        return next((v for v in ve.versions if v.version == ve.default_version), None)

    def deprecate(self, installation_id: str, endpoint: str, method: str, version: str) -> EndpointVersion:
        ve = self._endpoints.get((installation_id, method.upper(), endpoint))
        if ve is None: raise KeyError(f"Endpoint not found")
        for v in ve.versions:
            if v.version == version: v.status = "deprecated"; return v
        raise KeyError(f"Version {version} not found")

    def list_endpoints(self, installation_id: str) -> list[VersionedEndpoint]:
        return [ve for (inst, _, _), ve in self._endpoints.items() if inst == installation_id]
