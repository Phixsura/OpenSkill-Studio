"""Consumer API Explorer — interactive API endpoint discovery and testing."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ExplorerEndpoint:
    endpoint_id: str
    method: str
    path: str
    summary: str
    category: str = "general"
    auth_required: bool = True
    example_request: str = ""
    example_response: str = ""

@dataclass
class ExplorerCategory:
    name: str
    endpoints: list[ExplorerEndpoint] = field(default_factory=list)
    description: str = ""

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiExplorer:
    def __init__(self) -> None:
        self._endpoints: dict[tuple[str, str], ExplorerEndpoint] = {}

    def register(self, installation_id: str, endpoint: ExplorerEndpoint) -> ExplorerEndpoint:
        if not installation_id:
            raise ValueError("installation_id is required")
        if endpoint.method.upper() not in ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"):
            raise ValueError(f"Invalid method: {endpoint.method}")
        self._endpoints[(installation_id, endpoint.endpoint_id)] = endpoint
        return endpoint

    def search(self, installation_id: str, query: str) -> list[ExplorerEndpoint]:
        q = query.lower()
        return [e for (inst, _), e in self._endpoints.items() if inst == installation_id and (q in e.summary.lower() or q in e.path.lower() or q in e.category.lower())]

    def get_by_category(self, installation_id: str) -> list[ExplorerCategory]:
        endpoints = [e for (inst, _), e in self._endpoints.items() if inst == installation_id]
        cats: dict[str, list[ExplorerEndpoint]] = {}
        for e in endpoints:
            cats.setdefault(e.category, []).append(e)
        return sorted([ExplorerCategory(name=cat, endpoints=sorted(eps, key=lambda e: e.path)) for cat, eps in cats.items()], key=lambda c: c.name)

    def get(self, installation_id: str, endpoint_id: str) -> ExplorerEndpoint | None:
        return self._endpoints.get((installation_id, endpoint_id))

    def list_all(self, installation_id: str) -> list[ExplorerEndpoint]:
        return sorted([e for (inst, _), e in self._endpoints.items() if inst == installation_id], key=lambda e: e.path)
