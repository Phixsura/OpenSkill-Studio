"""Webhook Payload Transform — apply JSONPath-like transforms before delivery."""
from __future__ import annotations
from dataclasses import dataclass, field
import json
import structlog

log = structlog.get_logger()

@dataclass
class TransformRule:
    rule_id: str
    source_path: str   # dot-separated path e.g. "data.user.email"
    target_path: str   # dot-separated path for output
    default: str | None = None

@dataclass
class TransformConfig:
    config_id: str
    webhook_id: str
    rules: list[TransformRule] = field(default_factory=list)
    drop_unmapped: bool = False  # if True, only mapped fields appear in output

def _get_nested(obj: dict, path: str) -> object:
    parts = path.split(".")
    cur: object = obj
    for p in parts:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return None
    return cur

def _set_nested(obj: dict, path: str, value: object) -> None:
    parts = path.split(".")
    cur = obj
    for p in parts[:-1]:
        if p not in cur:
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookPayloadTransform:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], TransformConfig] = {}

    def set_config(self, installation_id: str, config: TransformConfig) -> TransformConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, config.config_id)
        self._configs[key] = config
        log.info("transform_config_set", installation_id=installation_id, config_id=config.config_id, rules=len(config.rules))
        return config

    def get_config(self, installation_id: str, config_id: str) -> TransformConfig | None:
        return self._configs.get((installation_id, config_id))

    def transform(self, installation_id: str, config_id: str, payload: dict) -> dict:
        config = self._configs.get((installation_id, config_id))
        if not config:
            return payload  # passthrough if no config
        if config.drop_unmapped:
            result: dict = {}
        else:
            result = json.loads(json.dumps(payload))  # deep copy
        for rule in config.rules:
            val = _get_nested(payload, rule.source_path)
            if val is None and rule.default is not None:
                val = rule.default
            if val is not None:
                _set_nested(result, rule.target_path, val)
        return result

    def list_configs(self, installation_id: str) -> list[TransformConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]
