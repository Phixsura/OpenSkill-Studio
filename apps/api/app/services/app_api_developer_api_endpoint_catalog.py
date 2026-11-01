"""App API Developer Endpoint Catalog — searchable catalog of all API endpoints."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class CatalogEndpoint:
    method: str
    path: str
    summary: str
    category: str = "general"
    auth_required: bool = True
    rate_limited: bool = True
    deprecated: bool = False

class AppAPIDeveloperAPIEndpointCatalog:
    def __init__(self) -> None:
        self._endpoints: dict[tuple[str, str, str], CatalogEndpoint] = {}

    def register(self, installation_id: str, method: str, path: str, summary: str, category: str = "general", auth_required: bool = True, rate_limited: bool = True, deprecated: bool = False) -> CatalogEndpoint:
        if not installation_id: raise ValueError("installation_id is required")
        ep = CatalogEndpoint(method=method.upper(), path=path, summary=summary, category=category, auth_required=auth_required, rate_limited=rate_limited, deprecated=deprecated)
        self._endpoints[(installation_id, method.upper(), path)] = ep
        return ep

    def search(self, installation_id: str, query: str) -> list[CatalogEndpoint]:
        q = query.lower()
        return [ep for (inst, _, _), ep in self._endpoints.items() if inst == installation_id and (q in ep.path.lower() or q in ep.summary.lower())]

    def by_category(self, installation_id: str, category: str) -> list[CatalogEndpoint]:
        return [ep for (inst, _, _), ep in self._endpoints.items() if inst == installation_id and ep.category == category]

    def stats(self, installation_id: str) -> dict:
        eps = [ep for (inst, _, _), ep in self._endpoints.items() if inst == installation_id]
        return {"total": len(eps), "deprecated": sum(1 for e in eps if e.deprecated), "categories": len(set(e.category for e in eps))}

    def list_all(self, installation_id: str) -> list[CatalogEndpoint]:
        return [ep for (inst, _, _), ep in self._endpoints.items() if inst == installation_id]
