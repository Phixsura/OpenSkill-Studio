"""Webhook Filter — filter and route webhook events based on rules.

Allows extensions to define filter rules that control which events
are delivered to their webhooks, reducing noise and cost.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class FilterRule:
    rule_id: str
    field: str       # payload field path, e.g. "event_type", "data.status"
    operator: str    # eq, neq, contains, startswith, in, exists
    value: str       # comparison value


@dataclass
class WebhookFilter:
    filter_id: str
    webhook_id: str
    rules: list[FilterRule]
    match_mode: str = "all"  # all = AND, any = OR


class WebhookFilterService:
    """Filters webhook events based on declarative rules."""

    def __init__(self):
        self._filters: dict[str, WebhookFilter] = {}

    def create_filter(self, filter_id: str, webhook_id: str,
                      rules: list[dict], match_mode: str = "all") -> WebhookFilter:
        parsed = [FilterRule(r.get("rule_id", f"r{i}"), r["field"], r["operator"], r["value"])
                  for i, r in enumerate(rules)]
        wf = WebhookFilter(filter_id, webhook_id, parsed, match_mode)
        self._filters[filter_id] = wf
        return wf

    def evaluate(self, filter_id: str, payload: dict) -> bool:
        """Check if payload matches the filter rules."""
        wf = self._filters.get(filter_id)
        if not wf:
            return True  # no filter = pass through

        results = [self._eval_rule(rule, payload) for rule in wf.rules]
        if wf.match_mode == "all":
            return all(results)
        return any(results)

    def _get_nested(self, data: dict, path: str) -> object | None:
        parts = path.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current

    def _eval_rule(self, rule: FilterRule, payload: dict) -> bool:
        value = self._get_nested(payload, rule.field)
        if rule.operator == "exists":
            return value is not None
        if value is None:
            return False
        str_val = str(value)
        if rule.operator == "eq":
            return str_val == rule.value
        elif rule.operator == "neq":
            return str_val != rule.value
        elif rule.operator == "contains":
            return rule.value in str_val
        elif rule.operator == "startswith":
            return str_val.startswith(rule.value)
        elif rule.operator == "in":
            return str_val in rule.value.split(",")
        return False

    def get_filter(self, filter_id: str) -> WebhookFilter | None:
        return self._filters.get(filter_id)

    def delete_filter(self, filter_id: str) -> bool:
        return self._filters.pop(filter_id, None) is not None

    def filter_events(self, filter_id: str, events: list[dict]) -> list[dict]:
        """Filter a batch of events, returning only matching ones."""
        return [e for e in events if self.evaluate(filter_id, e)]
