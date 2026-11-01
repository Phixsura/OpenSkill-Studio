"""App Service Catalog — catalog all services provided by an app.

Manages a service catalog for installed apps:
- Register services with descriptions and owners
- Track service health and dependencies
- Service categorization
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class CatalogService:
    """A service in the catalog."""

    service_id: str
    name: str
    description: str
    owner: str
    category: str = "uncategorized"
    health: str = "healthy"  # healthy, degraded, down
    dependencies: list[str] = field(default_factory=list)
    docs_url: str = ""


class AppServiceCatalog:
    """Catalog all services provided by an app."""

    def __init__(self) -> None:
        self._services: dict[tuple[str, str], CatalogService] = {}

    def register(
        self,
        installation_id: str,
        service_id: str,
        name: str,
        description: str,
        owner: str,
        category: str = "uncategorized",
        dependencies: list[str] | None = None,
        docs_url: str = "",
    ) -> CatalogService:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not service_id:
            raise ValueError("service_id is required")
        if not owner:
            raise ValueError("owner is required")

        svc = CatalogService(
            service_id=service_id, name=name, description=description,
            owner=owner, category=category,
            dependencies=dependencies or [], docs_url=docs_url,
        )
        self._services[(installation_id, service_id)] = svc
        return svc

    def update_health(
        self, installation_id: str, service_id: str, health: str
    ) -> CatalogService:
        if health not in ("healthy", "degraded", "down"):
            raise ValueError("health must be healthy, degraded, or down")
        svc = self._get(installation_id, service_id)
        svc.health = health
        return svc

    def list_services(
        self, installation_id: str, category: str | None = None
    ) -> list[CatalogService]:
        svcs = [s for (inst, _), s in self._services.items() if inst == installation_id]
        if category:
            svcs = [s for s in svcs if s.category == category]
        return svcs

    def get_categories(self, installation_id: str) -> list[str]:
        return sorted({
            s.category for (inst, _), s in self._services.items() if inst == installation_id
        })

    def service_count(self, installation_id: str) -> int:
        return sum(1 for (inst, _) in self._services if inst == installation_id)

    def _get(self, installation_id: str, service_id: str) -> CatalogService:
        key = (installation_id, service_id)
        s = self._services.get(key)
        if s is None:
            raise KeyError(f"Service {service_id} not found")
        return s
