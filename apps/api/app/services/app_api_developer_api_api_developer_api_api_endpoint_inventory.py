"""App API Developer API Endpoint Inventory — catalog all registered endpoints."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class EndpointEntry:
    endpoint_id: str
    method: str
    path: str
    version: str
    status: str = "active"  # "active", "deprecated", "beta", "internal"
    auth_required: bool = True
    rate_limited: bool = True
    documented: bool = False
    tags: list[str] = field(default_factory=list)

class AppAPIDeveloperAPIApiDeveloperApiApiEndpointInventory:
    def __init__(self) -> None:
        self._endpoints: dict[tuple[str, str], EndpointEntry] = {}

    def register(self, installation_id: str, endpoint_id: str, method: str, path: str, version: str, status: str = "active", auth_required: bool = True, rate_limited: bool = True, documented: bool = False, tags: list[str] | None = None) -> EndpointEntry:
        if not installation_id: raise ValueError("installation_id is required")
        if status not in ("active", "deprecated", "beta", "internal"): raise ValueError("invalid status")
        key = (installation_id, endpoint_id)
        if key in self._endpoints: raise ValueError(f"Endpoint {endpoint_id} exists")
        e = EndpointEntry(endpoint_id=endpoint_id, method=method.upper(), path=path, version=version, status=status, auth_required=auth_required, rate_limited=rate_limited, documented=documented, tags=tags or [])
        self._endpoints[key] = e
        return e

    def search(self, installation_id: str, path: str | None = None, version: str | None = None, status: str | None = None, tag: str | None = None) -> list[EndpointEntry]:
        endpoints = [e for (inst, _), e in self._endpoints.items() if inst == installation_id]
        if path: endpoints = [e for e in endpoints if path in e.path]
        if version: endpoints = [e for e in endpoints if e.version == version]
        if status: endpoints = [e for e in endpoints if e.status == status]
        if tag: endpoints = [e for e in endpoints if tag in e.tags]
        return endpoints

    def stats(self, installation_id: str) -> dict[str, int]:
        endpoints = [e for (inst, _), e in self._endpoints.items() if inst == installation_id]
        return {"total": len(endpoints), "active": sum(1 for e in endpoints if e.status == "active"), "deprecated": sum(1 for e in endpoints if e.status == "deprecated"), "documented": sum(1 for e in endpoints if e.documented), "undocumented": sum(1 for e in endpoints if not e.documented)}

    def all_endpoints(self, installation_id: str) -> list[EndpointEntry]:
        return [e for (inst, _), e in self._endpoints.items() if inst == installation_id]
