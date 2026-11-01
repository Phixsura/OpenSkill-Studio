"""API Consumer Webhook Event Transformer — transform event payloads per consumer."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class EventTransformRule:
    rule_id: str
    source_field: str
    target_field: str = ""
    operation: str = "copy"  # "copy", "rename", "remove", "default", "map"
    default_value: str = ""
    value_map: dict[str, str] = field(default_factory=dict)

@dataclass
class EventTransformConfig:
    consumer_id: str
    event_type: str
    rules: list[EventTransformRule] = field(default_factory=list)
    enabled: bool = True

VALID_OPS = {"copy", "rename", "remove", "default", "map"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventTransformer:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str, str], EventTransformConfig] = {}

    def configure(self, installation_id: str, config: EventTransformConfig) -> EventTransformConfig:
        if not installation_id: raise ValueError("installation_id is required")
        for r in config.rules:
            if r.operation not in VALID_OPS: raise ValueError(f"Invalid operation: {r.operation}")
        self._configs[(installation_id, config.consumer_id, config.event_type)] = config
        return config

    def transform(self, installation_id: str, consumer_id: str, event_type: str, payload: dict) -> dict:
        config = self._configs.get((installation_id, consumer_id, event_type))
        if config is None or not config.enabled: return dict(payload)
        result = dict(payload)
        for r in config.rules:
            if r.operation == "remove":
                result.pop(r.source_field, None)
            elif r.operation == "rename" and r.source_field in result:
                result[r.target_field or r.source_field] = result.pop(r.source_field)
            elif r.operation == "copy" and r.source_field in result:
                result[r.target_field] = result[r.source_field]
            elif r.operation == "default" and r.source_field not in result:
                result[r.source_field] = r.default_value
            elif r.operation == "map" and r.source_field in result:
                val = str(result[r.source_field])
                result[r.source_field] = r.value_map.get(val, val)
        return result

    def list_configs(self, installation_id: str) -> list[EventTransformConfig]:
        return [c for (inst, _, _), c in self._configs.items() if inst == installation_id]
