"""App API Developer Integration Hub — manage third-party integrations."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class Integration:
    integration_id: str
    name: str
    provider: str
    status: str = "connected"  # "connected", "disconnected", "error"
    event_count: int = 0

class AppAPIDeveloperAPIIntegrationHub:
    def __init__(self) -> None:
        self._integrations: dict[tuple[str, str], Integration] = {}

    def connect(self, installation_id: str, integration_id: str, name: str, provider: str) -> Integration:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, integration_id)
        if key in self._integrations: raise ValueError(f"Integration {integration_id} exists")
        i = Integration(integration_id=integration_id, name=name, provider=provider)
        self._integrations[key] = i
        return i

    def disconnect(self, installation_id: str, integration_id: str) -> Integration:
        i = self._get(installation_id, integration_id)
        i.status = "disconnected"
        return i

    def record_event(self, installation_id: str, integration_id: str) -> Integration:
        i = self._get(installation_id, integration_id)
        i.event_count += 1
        return i

    def connected(self, installation_id: str) -> list[Integration]:
        return [i for (inst, _), i in self._integrations.items() if inst == installation_id and i.status == "connected"]

    def list_integrations(self, installation_id: str) -> list[Integration]:
        return [i for (inst, _), i in self._integrations.items() if inst == installation_id]

    def _get(self, installation_id: str, integration_id: str) -> Integration:
        i = self._integrations.get((installation_id, integration_id))
        if i is None: raise KeyError(f"Integration {integration_id} not found")
        return i
