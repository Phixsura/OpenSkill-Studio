"""API Consumer Webhook Event Priority — assign priority levels to webhook events."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class EventPriorityRule:
    rule_id: str
    event_pattern: str  # "order.*", "payment.failed"
    priority: int  # 1 (highest) to 5 (lowest)
    description: str = ""

@dataclass
class PrioritizedEvent:
    event_id: str
    event_type: str
    priority: int
    matched_rule: str = ""

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventPriority:
    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], list[EventPriorityRule]] = {}

    def add_rule(self, installation_id: str, consumer_id: str, rule: EventPriorityRule) -> EventPriorityRule:
        if not installation_id: raise ValueError("installation_id is required")
        if not 1 <= rule.priority <= 5: raise ValueError("priority must be 1-5")
        self._rules.setdefault((installation_id, consumer_id), []).append(rule)
        return rule

    def get_priority(self, installation_id: str, consumer_id: str, event_type: str) -> PrioritizedEvent:
        rules = self._rules.get((installation_id, consumer_id), [])
        for r in sorted(rules, key=lambda x: x.priority):
            if self._matches(r.event_pattern, event_type):
                return PrioritizedEvent(event_id="", event_type=event_type, priority=r.priority, matched_rule=r.rule_id)
        return PrioritizedEvent(event_id="", event_type=event_type, priority=3)  # default medium

    def _matches(self, pattern: str, event_type: str) -> bool:
        if pattern == "*": return True
        if pattern.endswith(".*"):
            return event_type.startswith(pattern[:-2])
        return pattern == event_type

    def list_rules(self, installation_id: str, consumer_id: str) -> list[EventPriorityRule]:
        return self._rules.get((installation_id, consumer_id), [])

    def rule_count(self, installation_id: str) -> int:
        return sum(len(rs) for (inst, _), rs in self._rules.items() if inst == installation_id)
