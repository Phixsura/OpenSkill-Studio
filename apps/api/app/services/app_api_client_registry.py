"""App API Client Registry — register and manage API consumers.

Manages API client registrations:
- Register clients with metadata
- Track client status (active/suspended/revoked)
- Client statistics
- Per-installation scoped clients
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class ClientStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"


@dataclass
class APIClient:
    """A registered API client."""

    client_id: str
    name: str
    owner_email: str
    status: ClientStatus = ClientStatus.ACTIVE
    created_at: float = field(default_factory=time.time)
    request_count: int = 0
    last_active_at: float | None = None


class AppAPIClientRegistry:
    """Register and manage API consumers."""

    def __init__(self) -> None:
        self._clients: dict[tuple[str, str], APIClient] = {}

    def register(
        self, installation_id: str, client_id: str, name: str, owner_email: str,
    ) -> APIClient:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not owner_email or "@" not in owner_email:
            raise ValueError("valid owner_email is required")

        key = (installation_id, client_id)
        if key in self._clients:
            raise ValueError(f"Client {client_id} already registered")

        client = APIClient(client_id=client_id, name=name, owner_email=owner_email)
        self._clients[key] = client
        return client

    def record_activity(self, installation_id: str, client_id: str) -> APIClient:
        c = self._get(installation_id, client_id)
        c.request_count += 1
        c.last_active_at = time.time()
        return c

    def suspend(self, installation_id: str, client_id: str) -> APIClient:
        c = self._get(installation_id, client_id)
        c.status = ClientStatus.SUSPENDED
        return c

    def revoke(self, installation_id: str, client_id: str) -> APIClient:
        c = self._get(installation_id, client_id)
        c.status = ClientStatus.REVOKED
        return c

    def reactivate(self, installation_id: str, client_id: str) -> APIClient:
        c = self._get(installation_id, client_id)
        if c.status == ClientStatus.REVOKED:
            raise ValueError("Cannot reactivate revoked client")
        c.status = ClientStatus.ACTIVE
        return c

    def active_clients(self, installation_id: str) -> list[APIClient]:
        return [c for (inst, _), c in self._clients.items() if inst == installation_id and c.status == ClientStatus.ACTIVE]

    def list_clients(self, installation_id: str) -> list[APIClient]:
        return [c for (inst, _), c in self._clients.items() if inst == installation_id]

    def _get(self, installation_id: str, client_id: str) -> APIClient:
        key = (installation_id, client_id)
        c = self._clients.get(key)
        if c is None:
            raise KeyError(f"Client {client_id} not found")
        return c
