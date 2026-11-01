"""API Webhook Filter Rule — filter which events get delivered to consumers."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import structlog

log = structlog.get_logger()

@dataclass
class FilterRule:
    rule_id: str
    event_type: str  # glob pattern, e.g. "order.*", "user.created"
    field_match: dict[str, str] = field(default_factory=dict)  # field → regex
    action: str = "include"  # "include" or "exclude"

@dataclass
class FilterResult:
    event_type: str
    matched_rule_id: str | None
    delivered: bool

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookFilterRule:
    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], list[FilterRule]] = {}

    def add_rule(self, installation_id: str, consumer_id: str, rule: FilterRule) -> FilterRule:
        if not installation_id: raise ValueError("installation_id is required")
        if rule.action not in ("include", "exclude"): raise ValueError("action must be include or exclude")
        for pattern in rule.field_match.values():
            re.compile(pattern)  # validate regex
        self._rules.setdefault((installation_id, consumer_id), []).append(rule)
        return rule

    def evaluate(self, installation_id: str, consumer_id: str, event_type: str, event_data: dict) -> FilterResult:
        rules = self._rules.get((installation_id, consumer_id), [])
        if not rules:
            return FilterResult(event_type=event_type, matched_rule_id=None, delivered=True)
        
        # Check exclude rules first (deny wins)
        for r in rules:
            if r.action == "exclude" and self._matches(r, event_type, event_data):
                return FilterResult(event_type=event_type, matched_rule_id=r.rule_id, delivered=False)
        
        # Then check include rules
        include_rules = [r for r in rules if r.action == "include"]
        if not include_rules:
            return FilterResult(event_type=event_type, matched_rule_id=None, delivered=True)
        
        for r in include_rules:
            if self._matches(r, event_type, event_data):
                return FilterResult(event_type=event_type, matched_rule_id=r.rule_id, delivered=True)
        
        return FilterResult(event_type=event_type, matched_rule_id=None, delivered=False)

    def _matches(self, rule: FilterRule, event_type: str, event_data: dict) -> bool:
        # Convert glob to regex
        pattern = "^" + re.escape(rule.event_type).replace(r"\*", "[^.]*") + "$"
        if not re.match(pattern, event_type): return False
        for field_name, field_pattern in rule.field_match.items():
            val = str(event_data.get(field_name, ""))
            if not re.match(field_pattern, val): return False
        return True

    def rules_for(self, installation_id: str, consumer_id: str) -> list[FilterRule]:
        return self._rules.get((installation_id, consumer_id), [])

    def rule_count(self, installation_id: str) -> int:
        return sum(len(rs) for (inst, _), rs in self._rules.items() if inst == installation_id)
