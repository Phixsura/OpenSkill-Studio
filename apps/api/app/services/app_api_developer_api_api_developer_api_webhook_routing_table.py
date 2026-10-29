"""App API Developer Webhook Routing Table — advanced event-to-destination routing."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import structlog

log = structlog.get_logger()

@dataclass
class RoutingRule:
    rule_id: str
    event_pattern: str  # glob or regex
    destination: str
    transform: str = ""  # optional jq-like expression
    enabled: bool = True
    matches: int = 0

class AppAPIDeveloperAPIApiDeveloperApiWebhookRoutingTable:
    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], RoutingRule] = {}

    def add_rule(self, installation_id: str, rule_id: str, event_pattern: str, destination: str, transform: str = "") -> RoutingRule:
        if not installation_id: raise ValueError("installation_id is required")
        if not destination.startswith("https://"): raise ValueError("destination must use HTTPS")
        # Validate pattern as regex
        try:
            re.compile(event_pattern.replace("*", ".*"))
        except re.error:
            raise ValueError(f"Invalid pattern: {event_pattern}")
        key = (installation_id, rule_id)
        if key in self._rules: raise ValueError(f"Rule {rule_id} exists")
        r = RoutingRule(rule_id=rule_id, event_pattern=event_pattern, destination=destination, transform=transform)
        self._rules[key] = r
        return r

    def route(self, installation_id: str, event_type: str) -> list[RoutingRule]:
        matched = []
        for (inst, _), r in self._rules.items():
            if inst != installation_id or not r.enabled: continue
            pattern = r.event_pattern.replace("*", ".*")
            if re.fullmatch(pattern, event_type):
                r.matches += 1
                matched.append(r)
        return matched

    def toggle(self, installation_id: str, rule_id: str, enabled: bool) -> RoutingRule:
        key = (installation_id, rule_id)
        r = self._rules.get(key)
        if r is None: raise KeyError(f"Rule {rule_id} not found")
        r.enabled = enabled
        return r

    def all_rules(self, installation_id: str) -> list[RoutingRule]:
        return [r for (inst, _), r in self._rules.items() if inst == installation_id]

    def top_rules(self, installation_id: str, limit: int = 5) -> list[RoutingRule]:
        rules = self.all_rules(installation_id)
        return sorted(rules, key=lambda r: r.matches, reverse=True)[:limit]
