"""Consumer API Webhook Event Router — route events to different webhook endpoints by rules."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import structlog

log = structlog.get_logger()

@dataclass
class RoutingRule:
    rule_id: str
    event_pattern: str  # "order.*", "user.created"
    webhook_url: str
    priority: int = 0
    active: bool = True
    headers: dict[str, str] = field(default_factory=dict)

@dataclass
class RouteResult:
    event_type: str
    matched_rules: list[RoutingRule] = field(default_factory=list)
    unmatched: bool = False

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookEventRouter:
    def __init__(self) -> None:
        self._rules: dict[tuple[str, str, str], RoutingRule] = {}  # (inst, consumer, rule_id)

    def add_rule(self, installation_id: str, consumer_id: str, rule: RoutingRule) -> RoutingRule:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not rule.webhook_url.startswith("https://"):
            raise ValueError("webhook_url must use HTTPS")
        key = (installation_id, consumer_id, rule.rule_id)
        self._rules[key] = rule
        return rule

    def remove_rule(self, installation_id: str, consumer_id: str, rule_id: str) -> None:
        key = (installation_id, consumer_id, rule_id)
        if key not in self._rules:
            raise ValueError("Rule not found")
        del self._rules[key]

    def _matches(self, pattern: str, event_type: str) -> bool:
        if pattern == "*":
            return True
        if pattern.endswith(".*"):
            return event_type.startswith(pattern[:-2] + ".")
        return pattern == event_type

    def route(self, installation_id: str, consumer_id: str, event_type: str) -> RouteResult:
        matched: list[RoutingRule] = []
        for (inst, cid, _), rule in self._rules.items():
            if inst != installation_id or cid != consumer_id or not rule.active:
                continue
            if self._matches(rule.event_pattern, event_type):
                matched.append(rule)
        matched.sort(key=lambda r: -r.priority)
        return RouteResult(event_type=event_type, matched_rules=matched, unmatched=len(matched) == 0)

    def list_rules(self, installation_id: str, consumer_id: str) -> list[RoutingRule]:
        return sorted([r for (inst, cid, _), r in self._rules.items() if inst == installation_id and cid == consumer_id], key=lambda r: -r.priority)
