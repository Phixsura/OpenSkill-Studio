"""API Consumer Webhook Event Enricher — enrich webhook payloads with extra data."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class EnrichmentRule:
    rule_id: str
    field_name: str
    source: str  # "static", "lookup", "computed"
    value: str = ""  # for static
    lookup_key: str = ""  # for lookup

@dataclass
class EnrichmentConfig:
    consumer_id: str
    rules: list[EnrichmentRule] = field(default_factory=list)
    enabled: bool = True

VALID_SOURCES = {"static", "lookup", "computed", "timestamp", "consumer_info"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookEventEnricher:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], EnrichmentConfig] = {}
        self._lookups: dict[tuple[str, str], str] = {}  # (installation_id, key) → value

    def configure(self, installation_id: str, config: EnrichmentConfig) -> EnrichmentConfig:
        if not installation_id: raise ValueError("installation_id is required")
        for r in config.rules:
            if r.source not in VALID_SOURCES: raise ValueError(f"Invalid source: {r.source}")
        self._configs[(installation_id, config.consumer_id)] = config
        return config

    def set_lookup(self, installation_id: str, key: str, value: str) -> None:
        self._lookups[(installation_id, key)] = value

    def enrich(self, installation_id: str, consumer_id: str, payload: dict) -> dict:
        config = self._configs.get((installation_id, consumer_id))
        if config is None or not config.enabled: return dict(payload)
        result = dict(payload)
        for r in config.rules:
            if r.source == "static":
                result[r.field_name] = r.value
            elif r.source == "lookup":
                val = self._lookups.get((installation_id, r.lookup_key))
                if val: result[r.field_name] = val
            elif r.source == "timestamp":
                import time
                result[r.field_name] = int(time.time())
            elif r.source == "consumer_info":
                result[r.field_name] = consumer_id
        return result

    def list_configs(self, installation_id: str) -> list[EnrichmentConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]
