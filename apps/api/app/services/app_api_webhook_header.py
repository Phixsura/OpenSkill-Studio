"""App API Webhook Header — manage custom headers on webhook deliveries.

Manages webhook headers:
- Define custom headers per destination
- Secret header masking
- Header templates
- Per-installation scoped headers
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class WebhookHeader:
    """A custom webhook header."""

    name: str
    value: str
    secret: bool = False

    @property
    def masked_value(self) -> str:
        if not self.secret:
            return self.value
        if len(self.value) <= 4:
            return "****"
        return self.value[:2] + "*" * (len(self.value) - 4) + self.value[-2:]


@dataclass
class HeaderConfig:
    """Headers for a webhook destination."""

    destination: str
    headers: list[WebhookHeader] = field(default_factory=list)


class AppAPIWebhookHeader:
    """Manage custom headers on webhook deliveries."""

    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], HeaderConfig] = {}

    def set_headers(
        self, installation_id: str, destination: str, headers: list[dict],
    ) -> HeaderConfig:
        if not installation_id:
            raise ValueError("installation_id is required")

        header_objs = [
            WebhookHeader(name=h["name"], value=h["value"], secret=h.get("secret", False))
            for h in headers
        ]
        config = HeaderConfig(destination=destination, headers=header_objs)
        self._configs[(installation_id, destination)] = config
        return config

    def get_headers(self, installation_id: str, destination: str, mask: bool = True) -> list[dict]:
        config = self._configs.get((installation_id, destination))
        if config is None:
            return []
        return [
            {"name": h.name, "value": h.masked_value if mask else h.value, "secret": h.secret}
            for h in config.headers
        ]

    def list_destinations(self, installation_id: str) -> list[str]:
        return [dest for (inst, dest) in self._configs if inst == installation_id]
