"""API Consumer Webhook Event Router — route events to different endpoints by type."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class RoutingRule:
    rule_id: str
    event_pattern: str  # "order.*", "user.created"
    target_url: str
    priority: int = 0  # higher = checked first

@dataclass
class RoutingConfig:
    consumer_id: str
    rules: list[RoutingRule] = field(default_factory=list)
    default_url: str = ""

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookEventRouter:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], RoutingConfig] = {}

    def configure(self, installation_id: str, config: RoutingConfig) -> RoutingConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if not config.default_url and not config.rules: raise ValueError("Must have default_url or rules")
        config.rules.sort(key=lambda r: -r.priority)
        self._configs[(installation_id, config.consumer_id)] = config
        return config

    def route(self, installation_id: str, consumer_id: str, event_type: str) -> str | None:
        config = self._configs.get((installation_id, consumer_id))
        if config is None: return None
        for rule in config.rules:
            if self._matches(rule.event_pattern, event_type):
                return rule.target_url
        return config.default_url or None

    def _matches(self, pattern: str, event_type: str) -> bool:
        if pattern == "*": return True
        if "*" in pattern:
            prefix = pattern.rstrip("*").rstrip(".")
            return event_type.startswith(prefix)
        return pattern == event_type

    def list_configs(self, installation_id: str) -> list[RoutingConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]

    def rule_count(self, installation_id: str) -> int:
        return sum(len(c.rules) for (inst, _), c in self._configs.items() if inst == installation_id)
