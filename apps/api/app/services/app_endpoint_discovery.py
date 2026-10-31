"""App Endpoint Discovery — auto-discover and catalog API endpoints.

Manages endpoint discovery for installed apps:
- Register discovered endpoints
- Track endpoint metadata (auth, rate limit, deprecated)
- Categorize by tag
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class DiscoveredEndpoint:
    """A discovered API endpoint."""

    method: str
    path: str
    description: str = ""
    auth_required: bool = True
    rate_limited: bool = False
    deprecated: bool = False
    tags: list[str] = field(default_factory=list)


class AppEndpointDiscovery:
    """Auto-discover and catalog API endpoints."""

    def __init__(self) -> None:
        # installation_id → list[DiscoveredEndpoint]
        self._endpoints: dict[str, list[DiscoveredEndpoint]] = {}

    def register_endpoint(
        self,
        installation_id: str,
        method: str,
        path: str,
        description: str = "",
        auth_required: bool = True,
        rate_limited: bool = False,
        deprecated: bool = False,
        tags: list[str] | None = None,
    ) -> DiscoveredEndpoint:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not method or not path:
            raise ValueError("method and path required")

        ep = DiscoveredEndpoint(
            method=method.upper(), path=path, description=description,
            auth_required=auth_required, rate_limited=rate_limited,
            deprecated=deprecated, tags=tags or [],
        )
        endpoints = self._endpoints.setdefault(installation_id, [])
        # Replace if exists
        endpoints[:] = [e for e in endpoints if not (e.method == ep.method and e.path == ep.path)]
        endpoints.append(ep)
        return ep

    def list_endpoints(
        self, installation_id: str, tag: str | None = None, include_deprecated: bool = True
    ) -> list[DiscoveredEndpoint]:
        eps = self._endpoints.get(installation_id, [])
        if not include_deprecated:
            eps = [e for e in eps if not e.deprecated]
        if tag:
            eps = [e for e in eps if tag in e.tags]
        return eps

    def get_tags(self, installation_id: str) -> list[str]:
        tags: set[str] = set()
        for ep in self._endpoints.get(installation_id, []):
            tags.update(ep.tags)
        return sorted(tags)

    def endpoint_count(self, installation_id: str) -> int:
        return len(self._endpoints.get(installation_id, []))

    def deprecated_count(self, installation_id: str) -> int:
        return sum(1 for e in self._endpoints.get(installation_id, []) if e.deprecated)
