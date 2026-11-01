"""App API Deprecation — manage endpoint deprecation lifecycle.

Manages API deprecation:
- Mark endpoints as deprecated with sunset dates
- Track migration progress
- Generate deprecation headers
- Per-installation scoped deprecations
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class DeprecatedEndpoint:
    """A deprecated API endpoint."""

    endpoint_id: str
    method: str
    path: str
    sunset_at: float  # Unix timestamp when endpoint will be removed
    replacement: str = ""  # new endpoint path
    migration_guide: str = ""
    deprecated_at: float = field(default_factory=time.time)
    request_count: int = 0  # requests since deprecation

    @property
    def days_until_sunset(self) -> int:
        remaining = (self.sunset_at - time.time()) / 86400
        return max(0, int(remaining))

    @property
    def is_sunset(self) -> bool:
        return time.time() >= self.sunset_at


class AppAPIDeprecation:
    """Manage endpoint deprecation lifecycle."""

    def __init__(self) -> None:
        self._endpoints: dict[tuple[str, str], DeprecatedEndpoint] = {}

    def deprecate(
        self, installation_id: str, endpoint_id: str, method: str, path: str,
        sunset_at: float, replacement: str = "", migration_guide: str = "",
    ) -> DeprecatedEndpoint:
        if not installation_id:
            raise ValueError("installation_id is required")
        if sunset_at <= time.time():
            raise ValueError("sunset_at must be in the future")

        ep = DeprecatedEndpoint(
            endpoint_id=endpoint_id, method=method.upper(), path=path,
            sunset_at=sunset_at, replacement=replacement,
            migration_guide=migration_guide,
        )
        self._endpoints[(installation_id, endpoint_id)] = ep
        return ep

    def record_request(self, installation_id: str, endpoint_id: str) -> DeprecatedEndpoint:
        ep = self._get(installation_id, endpoint_id)
        ep.request_count += 1
        return ep

    def deprecation_headers(self, installation_id: str, endpoint_id: str) -> dict[str, str]:
        """Generate HTTP deprecation headers."""
        ep = self._get(installation_id, endpoint_id)
        headers = {"Deprecation": "true", "Sunset": str(int(ep.sunset_at))}
        if ep.replacement:
            headers["Link"] = f'<{ep.replacement}>; rel="successor-version"'
        return headers

    def sunset_endpoints(self, installation_id: str) -> list[DeprecatedEndpoint]:
        """Endpoints past their sunset date."""
        return [
            ep for (inst, _), ep in self._endpoints.items()
            if inst == installation_id and ep.is_sunset
        ]

    def active_deprecations(self, installation_id: str) -> list[DeprecatedEndpoint]:
        """Endpoints deprecated but not yet sunset."""
        return [
            ep for (inst, _), ep in self._endpoints.items()
            if inst == installation_id and not ep.is_sunset
        ]

    def list_all(self, installation_id: str) -> list[DeprecatedEndpoint]:
        return [ep for (inst, _), ep in self._endpoints.items() if inst == installation_id]

    def _get(self, installation_id: str, endpoint_id: str) -> DeprecatedEndpoint:
        key = (installation_id, endpoint_id)
        ep = self._endpoints.get(key)
        if ep is None:
            raise KeyError(f"Endpoint {endpoint_id} not found")
        return ep
