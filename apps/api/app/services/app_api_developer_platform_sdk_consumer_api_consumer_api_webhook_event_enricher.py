"""Consumer API Webhook Event Enricher — enrich webhook payloads with contextual data."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class EnrichmentRule:
    rule_id: str
    source_type: str  # "static", "lookup", "computed"
    target_field: str
    value: str = ""  # for static
    lookup_field: str = ""  # for lookup

@dataclass
class EnrichmentConfig:
    config_id: str
    webhook_id: str
    rules: list[EnrichmentRule] = field(default_factory=list)
    enabled: bool = True

@dataclass
class EnrichmentResult:
    original_fields: int
    enriched_fields: int
    rules_applied: int
    payload: dict

VALID_SOURCE_TYPES = {"static", "lookup", "computed"}

class AppAPIDeveloperPlatformSDKConsumerApiConsumerApiWebhookEventEnricher:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str, str], EnrichmentConfig] = {}
        self._lookup_data: dict[tuple[str, str], dict[str, str]] = {}  # (inst, key) -> values

    def set_config(self, installation_id: str, consumer_id: str, config: EnrichmentConfig) -> EnrichmentConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        for r in config.rules:
            if r.source_type not in VALID_SOURCE_TYPES:
                raise ValueError(f"Invalid source_type: {r.source_type}")
        self._configs[(installation_id, consumer_id, config.webhook_id)] = config
        return config

    def set_lookup_data(self, installation_id: str, key: str, data: dict[str, str]) -> None:
        self._lookup_data[(installation_id, key)] = data

    def enrich(self, installation_id: str, consumer_id: str, webhook_id: str, payload: dict) -> EnrichmentResult:
        config = self._configs.get((installation_id, consumer_id, webhook_id))
        if not config or not config.enabled:
            return EnrichmentResult(original_fields=len(payload), enriched_fields=0, rules_applied=0, payload=payload)
        result = dict(payload)
        applied = 0
        for rule in config.rules:
            if rule.source_type == "static":
                result[rule.target_field] = rule.value
                applied += 1
            elif rule.source_type == "lookup":
                lookup_key = str(payload.get(rule.lookup_field, ""))
                lookup_data = self._lookup_data.get((installation_id, lookup_key))
                if lookup_data and rule.target_field in lookup_data:
                    result[rule.target_field] = lookup_data[rule.target_field]
                    applied += 1
            elif rule.source_type == "computed":
                if rule.value == "payload_size":
                    import json
                    result[rule.target_field] = len(json.dumps(payload))
                    applied += 1
                elif rule.value == "field_count":
                    result[rule.target_field] = len(payload)
                    applied += 1
        enriched = len(result) - len(payload)
        return EnrichmentResult(original_fields=len(payload), enriched_fields=enriched, rules_applied=applied, payload=result)

    def get_config(self, installation_id: str, consumer_id: str, webhook_id: str) -> EnrichmentConfig | None:
        return self._configs.get((installation_id, consumer_id, webhook_id))
