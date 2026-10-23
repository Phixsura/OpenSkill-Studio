"""Flag evaluation engine — evaluate feature flags with targeting rules."""
from __future__ import annotations
import hashlib


def evaluate(flag_key: str, user: dict, rules: list[dict], default: bool = False) -> dict:
    for rule in rules:
        attr = rule.get("attribute", "")
        op = rule.get("operator", "eq")
        value = rule.get("value")
        user_val = user.get(attr)
        matched = False
        if op == "eq":
            matched = user_val == value
        elif op == "in":
            matched = user_val in (value if isinstance(value, list) else [value])
        elif op == "gt" and isinstance(user_val, (int, float)):
            matched = user_val > value
        elif op == "lt" and isinstance(user_val, (int, float)):
            matched = user_val < value
        if matched:
            return {"flag": flag_key, "enabled": rule.get("result", True),
                    "matched_rule": rule.get("name", ""), "reason": "rule_match"}
    # Percentage rollout fallback
    h = int(hashlib.md5(f"{flag_key}:{user.get('id', '')}".encode()).hexdigest(), 16)
    pct = (h % 10000) / 100
    rollout = rules[-1].get("rollout_pct", 0) if rules else 0
    if pct < rollout:
        return {"flag": flag_key, "enabled": True, "reason": "rollout"}
    return {"flag": flag_key, "enabled": default, "reason": "default"}
