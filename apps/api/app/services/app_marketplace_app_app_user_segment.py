"""User segment — audience segmentation for targeting."""

import html
from collections import defaultdict


def create_segment(*, name: str, rules: list[dict]) -> dict:
    conditions = []
    for r in rules:
        conditions.append({
            "field": r.get("field", ""),
            "operator": r.get("operator", "eq"),
            "value": r.get("value"),
            "label": html.escape(f"{r.get('field', '')} {r.get('operator', '')} {r.get('value', '')}"),
        })
    return {"name": html.escape(name), "rules": conditions,
            "rule_count": len(conditions), "match_type": "all"}


def evaluate_segment(*, user: dict, rules: list[dict]) -> dict:
    matched = []
    for r in rules:
        field = r.get("field", "")
        op = r.get("operator", "eq")
        val = r.get("value")
        user_val = user.get(field)
        if op == "eq" and user_val == val:
            matched.append(field)
        elif op == "gt" and isinstance(user_val, (int, float)) and user_val > val:
            matched.append(field)
        elif op == "lt" and isinstance(user_val, (int, float)) and user_val < val:
            matched.append(field)
        elif op == "in" and isinstance(val, list) and user_val in val:
            matched.append(field)
        elif op == "contains" and isinstance(user_val, str) and str(val) in user_val:
            matched.append(field)
    all_match = len(matched) == len(rules)
    return {"matches": all_match, "matched_rules": matched,
            "total_rules": len(rules), "match_pct": round(len(matched) / max(len(rules), 1) * 100)}
