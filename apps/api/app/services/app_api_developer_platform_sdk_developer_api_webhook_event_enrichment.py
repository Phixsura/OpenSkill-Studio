"""App API Developer Webhook Event Enrichment — enrich webhook payloads with metadata."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class EnrichmentRule:
    rule_id: str
    field_name: str
    source: str  # "static", "consumer", "timestamp", "request_id"
    value: str = ""
    applied_count: int = 0

class AppAPIDeveloperPlatformSDKDeveloperApiWebhookEventEnrichment:
    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], list[EnrichmentRule]] = {}

    def add_rule(self, installation_id: str, destination: str, rule_id: str, field_name: str, source: str, value: str = "") -> EnrichmentRule:
        if not installation_id: raise ValueError("installation_id is required")
        if source not in ("static", "consumer", "timestamp", "request_id"): raise ValueError("invalid source")
        r = EnrichmentRule(rule_id=rule_id, field_name=field_name, source=source, value=value)
        self._rules.setdefault((installation_id, destination), []).append(r)
        return r

    def enrich(self, installation_id: str, destination: str, payload: dict, consumer_id: str = "", request_id: str = "") -> dict:
        import time
        rules = self._rules.get((installation_id, destination), [])
        enriched = dict(payload)
        for r in rules:
            if r.source == "static": enriched[r.field_name] = r.value
            elif r.source == "consumer": enriched[r.field_name] = consumer_id
            elif r.source == "timestamp": enriched[r.field_name] = str(int(time.time()))
            elif r.source == "request_id": enriched[r.field_name] = request_id
            r.applied_count += 1
        return enriched

    def rules_for(self, installation_id: str, destination: str) -> list[EnrichmentRule]:
        return self._rules.get((installation_id, destination), [])

    def total_enrichments(self, installation_id: str) -> int:
        return sum(r.applied_count for rules in self._rules.values() for r in rules if rules and self._rules)
