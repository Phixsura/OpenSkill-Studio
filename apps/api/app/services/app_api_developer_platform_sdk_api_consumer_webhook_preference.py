"""App API Developer Consumer Webhook Preference — per-consumer webhook delivery preferences."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class WebhookPreference:
    consumer_id: str
    preferred_format: str = "json"  # "json", "xml", "form"
    preferred_encoding: str = "utf-8"
    include_headers: list[str] = field(default_factory=list)
    batch_enabled: bool = False
    max_batch_size: int = 10
    compression: str = "none"  # "none", "gzip", "deflate"

class AppAPIDeveloperPlatformSDKApiConsumerWebhookPreference:
    def __init__(self) -> None:
        self._prefs: dict[tuple[str, str], WebhookPreference] = {}

    def set(self, installation_id: str, consumer_id: str, **kwargs) -> WebhookPreference:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, consumer_id)
        p = WebhookPreference(consumer_id=consumer_id)
        for k, v in kwargs.items():
            if hasattr(p, k): setattr(p, k, v)
        if p.preferred_format not in ("json", "xml", "form"): raise ValueError("invalid format")
        if p.compression not in ("none", "gzip", "deflate"): raise ValueError("invalid compression")
        self._prefs[key] = p
        return p

    def get(self, installation_id: str, consumer_id: str) -> WebhookPreference:
        return self._prefs.get((installation_id, consumer_id), WebhookPreference(consumer_id=consumer_id))

    def batch_enabled_consumers(self, installation_id: str) -> list[WebhookPreference]:
        return [p for (inst, _), p in self._prefs.items() if inst == installation_id and p.batch_enabled]

    def format_distribution(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _), p in self._prefs.items():
            if inst == installation_id: counts[p.preferred_format] = counts.get(p.preferred_format, 0) + 1
        return counts

    def all_preferences(self, installation_id: str) -> list[WebhookPreference]:
        return [p for (inst, _), p in self._prefs.items() if inst == installation_id]
