"""App API Developer Webhook Content Type Manager — manage payload content types."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

VALID_CONTENT_TYPES = {"application/json", "application/xml", "application/x-www-form-urlencoded", "text/plain", "application/cloudevents+json"}

@dataclass
class ContentTypeConfig:
    destination: str
    content_type: str = "application/json"
    charset: str = "utf-8"
    delivery_count: int = 0

class AppAPIDeveloperAPIWebhookContentTypeManager:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], ContentTypeConfig] = {}

    def configure(self, installation_id: str, destination: str, content_type: str, charset: str = "utf-8") -> ContentTypeConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if content_type not in VALID_CONTENT_TYPES: raise ValueError(f"Unsupported: {content_type}")
        if charset not in ("utf-8", "ascii", "iso-8859-1"): raise ValueError(f"Unsupported charset: {charset}")
        key = (installation_id, destination)
        c = ContentTypeConfig(destination=destination, content_type=content_type, charset=charset)
        self._configs[key] = c
        return c

    def get_content_type(self, installation_id: str, destination: str) -> str:
        key = (installation_id, destination)
        c = self._configs.get(key)
        return f"{c.content_type}; charset={c.charset}" if c else "application/json; charset=utf-8"

    def record_delivery(self, installation_id: str, destination: str) -> None:
        key = (installation_id, destination)
        c = self._configs.get(key)
        if c: c.delivery_count += 1

    def list_configs(self, installation_id: str) -> list[ContentTypeConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]

    def by_content_type(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _), c in self._configs.items():
            if inst == installation_id:
                counts[c.content_type] = counts.get(c.content_type, 0) + 1
        return counts
