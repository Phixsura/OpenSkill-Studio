"""Webhook filter engine — filter webhook events before delivery."""
from __future__ import annotations
import re


def create_filter(name: str, rules: list[dict]) -> dict:
    return {"name": name, "rules": rules, "rule_count": len(rules)}


def apply_filter(filter_config: dict, event: dict) -> dict:
    for rule in filter_config["rules"]:
        field = rule.get("field", "")
        operator = rule.get("operator", "eq")
        value = rule.get("value")
        event_val = event.get(field)
        matched = False
        if operator == "eq":
            matched = event_val == value
        elif operator == "neq":
            matched = event_val != value
        elif operator == "contains" and isinstance(event_val, str):
            matched = value in event_val
        elif operator == "regex" and isinstance(event_val, str):
            matched = bool(re.search(value, event_val))
        elif operator == "in" and isinstance(value, list):
            matched = event_val in value
        action = rule.get("action", "include")
        if matched and action == "exclude":
            return {"delivered": False, "reason": f"excluded by rule: {rule.get('name', '')}"}
        if matched and action == "include":
            return {"delivered": True, "matched_rule": rule.get("name", "")}
    return {"delivered": True, "matched_rule": "default"}
