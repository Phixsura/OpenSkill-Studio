"""App API Webhook Routing Rule — route events to destinations by rules."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class RoutingRule:
    rule_id: str
    event_pattern: str
    destination: str
    priority: int = 0
    enabled: bool = True
    routed_count: int = 0

class AppAPIWebhookRoutingRule:
    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], RoutingRule] = {}

    def add_rule(self, installation_id: str, rule_id: str, event_pattern: str, destination: str, priority: int = 0) -> RoutingRule:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, rule_id)
        if key in self._rules: raise ValueError(f"Rule {rule_id} already exists")
        r = RoutingRule(rule_id=rule_id, event_pattern=event_pattern, destination=destination, priority=priority)
        self._rules[key] = r
        return r

    def route(self, installation_id: str, event_type: str) -> list[str]:
        """Find matching destinations for event, sorted by priority."""
        matches = []
        for (inst, _), r in self._rules.items():
            if inst != installation_id or not r.enabled: continue
            if r.event_pattern == "*" or r.event_pattern == event_type or (r.event_pattern.endswith(".*") and event_type.startswith(r.event_pattern[:-2] + ".")):
                r.routed_count += 1
                matches.append((r.priority, r.destination))
        matches.sort(key=lambda x: x[0], reverse=True)
        return [d for _, d in matches]

    def list_rules(self, installation_id: str) -> list[RoutingRule]:
        return [r for (inst, _), r in self._rules.items() if inst == installation_id]
