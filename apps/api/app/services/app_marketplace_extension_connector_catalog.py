"""Connector Catalog — browsable catalog of available connectors."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Connector:
    connector_id: str
    name: str
    provider: str
    category: str  # crm, analytics, storage, communication, payment
    auth_type: str = "oauth2"  # oauth2, api_key, basic, none
    description: str = ""
    icon: str = "🔌"
    installed_count: int = 0
    status: str = "available"  # available, beta, deprecated


class ConnectorCatalogService:
    def __init__(self):
        self._connectors: dict[str, Connector] = {}

    def register(self, connector_id: str, name: str, provider: str,
                 category: str, auth_type: str = "oauth2", **kwargs) -> Connector:
        c = Connector(connector_id=connector_id, name=name, provider=provider,
                      category=category, auth_type=auth_type, **kwargs)
        self._connectors[connector_id] = c
        return c

    def browse(self, category: str | None = None, query: str | None = None) -> list[Connector]:
        results = list(self._connectors.values())
        if category:
            results = [c for c in results if c.category == category]
        if query:
            q = query.lower()
            results = [c for c in results if q in c.name.lower() or q in c.provider.lower()]
        return sorted(results, key=lambda c: c.installed_count, reverse=True)

    def get(self, connector_id: str) -> Connector | None:
        return self._connectors.get(connector_id)

    def get_categories(self) -> dict[str, int]:
        cats: dict[str, int] = {}
        for c in self._connectors.values():
            cats[c.category] = cats.get(c.category, 0) + 1
        return cats

    def increment_installs(self, connector_id: str) -> bool:
        c = self._connectors.get(connector_id)
        if c:
            c.installed_count += 1
            return True
        return False
