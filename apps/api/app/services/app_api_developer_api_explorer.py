"""App API Developer API Explorer — interactive API exploration tool."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ExplorerEndpoint:
    method: str
    path: str
    summary: str
    category: str = "general"
    try_it_enabled: bool = True

class AppAPIDeveloperAPIExplorer:
    def __init__(self) -> None:
        self._endpoints: dict[tuple[str, str, str], ExplorerEndpoint] = {}

    def register(self, installation_id: str, method: str, path: str, summary: str, category: str = "general", try_it: bool = True) -> ExplorerEndpoint:
        if not installation_id: raise ValueError("installation_id is required")
        ep = ExplorerEndpoint(method=method.upper(), path=path, summary=summary, category=category, try_it_enabled=try_it)
        self._endpoints[(installation_id, method.upper(), path)] = ep
        return ep

    def by_category(self, installation_id: str, category: str) -> list[ExplorerEndpoint]:
        return [ep for (inst, _, _), ep in self._endpoints.items() if inst == installation_id and ep.category == category]

    def categories(self, installation_id: str) -> list[str]:
        cats: set[str] = set()
        for (inst, _, _), ep in self._endpoints.items():
            if inst == installation_id: cats.add(ep.category)
        return sorted(cats)

    def search(self, installation_id: str, query: str) -> list[ExplorerEndpoint]:
        q = query.lower()
        return [ep for (inst, _, _), ep in self._endpoints.items() if inst == installation_id and (q in ep.path.lower() or q in ep.summary.lower())]

    def list_endpoints(self, installation_id: str) -> list[ExplorerEndpoint]:
        return [ep for (inst, _, _), ep in self._endpoints.items() if inst == installation_id]
