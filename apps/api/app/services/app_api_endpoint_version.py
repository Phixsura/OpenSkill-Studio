"""App API Endpoint Version — track per-endpoint version mappings.

Manages endpoint versions:
- Map endpoints to their API version
- Track which version each endpoint belongs to
- Compare endpoints across versions
- Per-installation scoped mappings
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class EndpointVersion:
    """An endpoint's version mapping."""

    method: str
    path: str
    version: str
    deprecated: bool = False


class AppAPIEndpointVersion:
    """Track per-endpoint version mappings."""

    def __init__(self) -> None:
        self._endpoints: dict[tuple[str, str, str, str], EndpointVersion] = {}

    def register(
        self, installation_id: str, method: str, path: str,
        version: str, deprecated: bool = False,
    ) -> EndpointVersion:
        if not installation_id:
            raise ValueError("installation_id is required")
        ev = EndpointVersion(method=method.upper(), path=path, version=version, deprecated=deprecated)
        self._endpoints[(installation_id, version, method.upper(), path)] = ev
        return ev

    def endpoints_for_version(self, installation_id: str, version: str) -> list[EndpointVersion]:
        return [
            ep for (inst, v, _, _), ep in self._endpoints.items()
            if inst == installation_id and v == version
        ]

    def versions_for_endpoint(self, installation_id: str, method: str, path: str) -> list[str]:
        return sorted([
            v for (inst, v, m, p) in self._endpoints
            if inst == installation_id and m == method.upper() and p == path
        ])

    def deprecated_endpoints(self, installation_id: str) -> list[EndpointVersion]:
        return [ep for (inst, _, _, _), ep in self._endpoints.items() if inst == installation_id and ep.deprecated]

    def list_all(self, installation_id: str) -> list[EndpointVersion]:
        return [ep for (inst, _, _, _), ep in self._endpoints.items() if inst == installation_id]
