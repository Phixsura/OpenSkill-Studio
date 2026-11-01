"""API Consumer Response Transformer — transform API responses per consumer."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class TransformRule:
    rule_id: str
    operation: str  # "rename", "remove", "add", "format", "flatten"
    source_field: str
    target_field: str = ""
    value: str = ""

@dataclass
class TransformConfig:
    consumer_id: str
    rules: list[TransformRule] = field(default_factory=list)
    enabled: bool = True

VALID_OPS = {"rename", "remove", "add", "format", "flatten", "mask"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponseTransformer:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], TransformConfig] = {}
        self._stats: dict[str, dict[str, int]] = {}

    def configure(self, installation_id: str, config: TransformConfig) -> TransformConfig:
        if not installation_id: raise ValueError("installation_id is required")
        for r in config.rules:
            if r.operation not in VALID_OPS: raise ValueError(f"Invalid operation: {r.operation}")
        self._configs[(installation_id, config.consumer_id)] = config
        return config

    def transform(self, installation_id: str, consumer_id: str, response: dict) -> dict:
        config = self._configs.get((installation_id, consumer_id))
        if config is None or not config.enabled: return dict(response)
        result = dict(response)
        for r in config.rules:
            if r.operation == "remove": result.pop(r.source_field, None)
            elif r.operation == "rename" and r.source_field in result:
                result[r.target_field or r.source_field] = result.pop(r.source_field)
            elif r.operation == "add":
                result[r.source_field] = r.value
            elif r.operation == "mask" and r.source_field in result:
                val = str(result[r.source_field])
                result[r.source_field] = "***" + val[-4:] if len(val) > 4 else "***"
        stats = self._stats.setdefault(installation_id, {"transformed": 0})
        stats["transformed"] += 1
        return result

    def list_configs(self, installation_id: str) -> list[TransformConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]
