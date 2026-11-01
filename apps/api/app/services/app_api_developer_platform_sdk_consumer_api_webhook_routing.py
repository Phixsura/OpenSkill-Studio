"""Consumer API Webhook Routing — content-based webhook routing with filters."""
from __future__ import annotations

import re
import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class RoutingRule:
    rule_id: str
    name: str
    field_path: str  # dot-separated path in payload
    operator: str  # eq, neq, contains, gt, lt, regex, exists
    value: str = ""
    target_url: str = ""
    priority: int = 0


@dataclass
class WebhookRouter:
    """Route webhooks based on payload content with configurable rules."""

    _rules: list[RoutingRule] = field(default_factory=list)
    _default_url: str = ""
    _route_count: int = 0

    def set_default(self, url: str) -> dict:
        self._default_url = url
        return {"default_url": url}

    def add_rule(self, rule: RoutingRule) -> dict:
        valid_ops = ("eq", "neq", "contains", "gt", "lt", "regex", "exists")
        if rule.operator not in valid_ops:
            raise ValueError(f"Invalid operator: {rule.operator}")
        if not rule.target_url.startswith("http"):
            raise ValueError("target_url must start with http")
        self._rules.append(rule)
        self._rules.sort(key=lambda r: r.priority, reverse=True)
        logger.info("routing_rule_added", rule_id=rule.rule_id)
        return {"rule_id": rule.rule_id, "total_rules": len(self._rules)}

    def _get_field(self, payload: dict, path: str):
        parts = path.split(".")
        val = payload
        for p in parts:
            if isinstance(val, dict) and p in val:
                val = val[p]
            else:
                return None
        return val

    def _matches(self, rule: RoutingRule, payload: dict) -> bool:
        val = self._get_field(payload, rule.field_path)
        if rule.operator == "exists":
            return val is not None
        if val is None:
            return False
        str_val = str(val)
        if rule.operator == "eq":
            return str_val == rule.value
        elif rule.operator == "neq":
            return str_val != rule.value
        elif rule.operator == "contains":
            return rule.value in str_val
        elif rule.operator == "gt":
            try:
                return float(str_val) > float(rule.value)
            except ValueError:
                return False
        elif rule.operator == "lt":
            try:
                return float(str_val) < float(rule.value)
            except ValueError:
                return False
        elif rule.operator == "regex":
            try:
                return bool(re.search(rule.value, str_val))
            except re.error:
                return False
        return False

    def route(self, payload: dict) -> dict:
        self._route_count += 1
        matched = []
        for rule in self._rules:
            if self._matches(rule, payload):
                matched.append({"rule_id": rule.rule_id, "target_url": rule.target_url,
                                "name": rule.name})
        if matched:
            return {"routed": True, "target_url": matched[0]["target_url"],
                    "matched_rules": matched, "match_count": len(matched)}
        if self._default_url:
            return {"routed": True, "target_url": self._default_url,
                    "matched_rules": [], "match_count": 0, "default": True}
        return {"routed": False, "reason": "no_matching_rule"}

    def remove_rule(self, rule_id: str) -> dict:
        before = len(self._rules)
        self._rules = [r for r in self._rules if r.rule_id != rule_id]
        return {"removed": before > len(self._rules)}

    def list_rules(self) -> list[dict]:
        return [
            {"rule_id": r.rule_id, "name": r.name, "field": r.field_path,
             "operator": r.operator, "value": r.value, "priority": r.priority}
            for r in self._rules
        ]

    def get_stats(self) -> dict:
        return {"total_rules": len(self._rules), "total_routed": self._route_count,
                "has_default": bool(self._default_url)}
