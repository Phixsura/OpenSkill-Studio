"""App API Service Mesh — manage service-to-service communication.

Manages service mesh:
- Register services with endpoints
- Define communication policies
- Track inter-service call metrics
- Per-installation scoped meshes
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class MeshService:
    """A service in the mesh."""

    service_id: str
    name: str
    endpoint: str
    call_count: int = 0
    error_count: int = 0

    @property
    def error_rate(self) -> float:
        total = self.call_count + self.error_count
        if total == 0:
            return 0.0
        return round(self.error_count / total * 100, 1)


@dataclass
class ServiceLink:
    """A communication link between services."""

    source: str
    target: str
    call_count: int = 0


class AppAPIServiceMesh:
    """Manage service-to-service communication."""

    def __init__(self) -> None:
        self._services: dict[tuple[str, str], MeshService] = {}
        self._links: dict[tuple[str, str, str], ServiceLink] = {}

    def register_service(
        self, installation_id: str, service_id: str, name: str, endpoint: str,
    ) -> MeshService:
        if not installation_id:
            raise ValueError("installation_id is required")
        svc = MeshService(service_id=service_id, name=name, endpoint=endpoint)
        self._services[(installation_id, service_id)] = svc
        return svc

    def record_call(
        self, installation_id: str, source_id: str, target_id: str, success: bool,
    ) -> ServiceLink:
        # Update target metrics
        tgt = self._services.get((installation_id, target_id))
        if tgt:
            if success:
                tgt.call_count += 1
            else:
                tgt.error_count += 1

        # Update link
        lkey = (installation_id, source_id, target_id)
        if lkey not in self._links:
            self._links[lkey] = ServiceLink(source=source_id, target=target_id)
        self._links[lkey].call_count += 1
        return self._links[lkey]

    def list_services(self, installation_id: str) -> list[MeshService]:
        return [s for (inst, _), s in self._services.items() if inst == installation_id]

    def list_links(self, installation_id: str) -> list[ServiceLink]:
        return [l for (inst, _, _), l in self._links.items() if inst == installation_id]

    def service_links(self, installation_id: str, service_id: str) -> list[ServiceLink]:
        return [l for (inst, src, _), l in self._links.items() if inst == installation_id and src == service_id]
