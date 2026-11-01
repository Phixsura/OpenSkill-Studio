"""App Webhook Filter — filter webhook events before delivery.

Manages webhook event filters:
- Define include/exclude rules per event type
- Field-level matching conditions
- Priority-ordered rule evaluation
- Per-installation scoped filters
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class FilterRule:
    """A webhook filter rule."""

    rule_id: str
    event_type: str  # "*" for all
    action: str  # "include" or "exclude"
    field: str | None = None  # dot-path, e.g. "data.status"
    operator: str = "eq"  # "eq", "ne", "contains", "exists"
    value: str | None = None
    priority: int = 0


class AppWebhookFilter:
    """Filter webhook events before delivery."""

    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], FilterRule] = {}

    def add_rule(
        self, installation_id: str, rule_id: str, event_type: str,
        action: str, field: str | None = None, operator: str = "eq",
        value: str | None = None, priority: int = 0,
    ) -> FilterRule:
        if not installation_id:
            raise ValueError("installation_id is required")
        if action not in ("include", "exclude"):
            raise ValueError("action must be include or exclude")
        if operator not in ("eq", "ne", "contains", "exists"):
            raise ValueError("invalid operator")

        rule = FilterRule(
            rule_id=rule_id, event_type=event_type, action=action,
            field=field, operator=operator, value=value, priority=priority,
        )
        self._rules[(installation_id, rule_id)] = rule
        return rule

    def should_deliver(
        self, installation_id: str, event_type: str, payload: dict,
    ) -> bool:
        """Evaluate rules in priority order. First matching rule wins."""
        rules = sorted(
            [r for (inst, _), r in self._rules.items() if inst == installation_id],
            key=lambda r: r.priority, reverse=True,
        )

        for rule in rules:
            if rule.event_type != "*" and rule.event_type != event_type:
                continue
            if rule.field is None:
                # Type-only rule
                return rule.action == "include"
            if self._matches(rule, payload):
                return rule.action == "include"

        return True  # default: deliver if no rules match

    def remove_rule(self, installation_id: str, rule_id: str) -> bool:
        key = (installation_id, rule_id)
        if key in self._rules:
            del self._rules[key]
            return True
        return False

    def list_rules(self, installation_id: str) -> list[FilterRule]:
        rules = [r for (inst, _), r in self._rules.items() if inst == installation_id]
        return sorted(rules, key=lambda r: r.priority, reverse=True)

    def _matches(self, rule: FilterRule, payload: dict) -> bool:
        if rule.field is None:
            return True
        val = self._resolve_field(payload, rule.field)

        if rule.operator == "exists":
            return val is not None
        if val is None:
            return False

        str_val = str(val)
        if rule.operator == "eq":
            return str_val == rule.value
        if rule.operator == "ne":
            return str_val != rule.value
        if rule.operator == "contains":
            return rule.value is not None and rule.value in str_val
        return False

    def _resolve_field(self, payload: dict, path: str) -> object | None:
        parts = path.split(".")
        current: object = payload
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current
