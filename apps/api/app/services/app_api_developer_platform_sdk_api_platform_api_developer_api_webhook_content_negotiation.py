"""App API Developer Webhook Content Negotiation — negotiate payload format per consumer."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

SUPPORTED_FORMATS = {"application/json", "application/xml", "application/cloudevents+json", "application/x-www-form-urlencoded"}

@dataclass
class ContentNegotiation:
    consumer_id: str
    preferred_format: str = "application/json"
    accepted_formats: list[str] = None
    fallback_format: str = "application/json"
    negotiations: int = 0

    def __post_init__(self):
        if self.accepted_formats is None:
            self.accepted_formats = ["application/json"]

class AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiWebhookContentNegotiation:
    def __init__(self) -> None:
        self._negotiations: dict[tuple[str, str], ContentNegotiation] = {}

    def configure(self, installation_id: str, consumer_id: str, preferred_format: str, accepted_formats: list[str] | None = None) -> ContentNegotiation:
        if not installation_id: raise ValueError("installation_id is required")
        if preferred_format not in SUPPORTED_FORMATS: raise ValueError(f"Unsupported format: {preferred_format}")
        key = (installation_id, consumer_id)
        n = ContentNegotiation(consumer_id=consumer_id, preferred_format=preferred_format, accepted_formats=accepted_formats or [preferred_format])
        self._negotiations[key] = n
        return n

    def negotiate(self, installation_id: str, consumer_id: str, available_formats: list[str]) -> str:
        key = (installation_id, consumer_id)
        n = self._negotiations.get(key)
        if n is None: return "application/json"
        n.negotiations += 1
        if n.preferred_format in available_formats: return n.preferred_format
        for fmt in (n.accepted_formats or []):
            if fmt in available_formats: return fmt
        return n.fallback_format

    def format_distribution(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _), n in self._negotiations.items():
            if inst == installation_id:
                counts[n.preferred_format] = counts.get(n.preferred_format, 0) + 1
        return counts

    def all_negotiations(self, installation_id: str) -> list[ContentNegotiation]:
        return [n for (inst, _), n in self._negotiations.items() if inst == installation_id]
