"""App API Webhook Content Type — manage webhook payload content types.

Manages content type preferences:
- Configure preferred content type per destination
- Supported types (json, form, xml)
- Default content type
- Per-installation scoped configs
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

log = structlog.get_logger()

VALID_TYPES = {"application/json", "application/x-www-form-urlencoded", "application/xml", "text/plain"}


@dataclass
class ContentTypeConfig:
    """Content type configuration for a destination."""

    destination: str
    content_type: str
    delivery_count: int = 0


class AppAPIWebhookContentType:
    """Manage webhook payload content types."""

    def __init__(self, default_type: str = "application/json") -> None:
        self._default = default_type
        self._configs: dict[tuple[str, str], ContentTypeConfig] = {}

    def configure(
        self, installation_id: str, destination: str, content_type: str,
    ) -> ContentTypeConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if content_type not in VALID_TYPES:
            raise ValueError(f"content_type must be one of {VALID_TYPES}")

        config = ContentTypeConfig(destination=destination, content_type=content_type)
        self._configs[(installation_id, destination)] = config
        return config

    def get_content_type(self, installation_id: str, destination: str) -> str:
        config = self._configs.get((installation_id, destination))
        return config.content_type if config else self._default

    def record_delivery(self, installation_id: str, destination: str) -> None:
        config = self._configs.get((installation_id, destination))
        if config:
            config.delivery_count += 1

    def list_configs(self, installation_id: str) -> list[ContentTypeConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]
