"""Consumer API Endpoint Inventory — catalog all available API endpoints."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class EndpointEntry:
    endpoint_id: str
    method: str
    path: str
    version: str = "v1"
    status: str = "active"  # "active", "deprecated", "beta", "internal"
    auth_type: str = "api_key"  # "api_key", "oauth2", "none"
    rate_limit_rps: int = 0
    tags: list[str] = field(default_factory=list)
    description: str = ""

@dataclass
class InventorySummary:
    total_endpoints: int
    by_method: dict[str, int]
    by_status: dict[str, int]
    by_version: dict[str, int]

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiEndpointInventory:
    def __init__(self) -> None:
        self._endpoints: dict[tuple[str, str], EndpointEntry] = {}

    def register(self, installation_id: str, entry: EndpointEntry) -> EndpointEntry:
        if not installation_id:
            raise ValueError("installation_id is required")
        if entry.method.upper() not in ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"):
            raise ValueError(f"Invalid method: {entry.method}")
        if entry.status not in ("active", "deprecated", "beta", "internal"):
            raise ValueError(f"Invalid status: {entry.status}")
        self._endpoints[(installation_id, entry.endpoint_id)] = entry
        return entry

    def get(self, installation_id: str, endpoint_id: str) -> EndpointEntry | None:
        return self._endpoints.get((installation_id, endpoint_id))

    def search(self, installation_id: str, query: str = "", tag: str = "", status: str = "") -> list[EndpointEntry]:
        results = [e for (inst, _), e in self._endpoints.items() if inst == installation_id]
        if query:
            q = query.lower()
            results = [e for e in results if q in e.path.lower() or q in e.description.lower()]
        if tag:
            results = [e for e in results if tag in e.tags]
        if status:
            results = [e for e in results if e.status == status]
        return sorted(results, key=lambda e: e.path)

    def get_summary(self, installation_id: str) -> InventorySummary:
        entries = [e for (inst, _), e in self._endpoints.items() if inst == installation_id]
        by_method: dict[str, int] = {}
        by_status: dict[str, int] = {}
        by_version: dict[str, int] = {}
        for e in entries:
            by_method[e.method] = by_method.get(e.method, 0) + 1
            by_status[e.status] = by_status.get(e.status, 0) + 1
            by_version[e.version] = by_version.get(e.version, 0) + 1
        return InventorySummary(total_endpoints=len(entries), by_method=by_method, by_status=by_status, by_version=by_version)
