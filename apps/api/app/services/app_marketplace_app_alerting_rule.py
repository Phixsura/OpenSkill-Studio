"""Alerting rule — define conditions that trigger alerts."""

import secrets


OPERATORS = {"gt": ">", "gte": ">=", "lt": "<", "lte": "<=", "eq": "==", "ne": "!="}


def create_alert_rule(*, name: str, metric: str, operator: str,
                        threshold: float, duration_sec: int = 60,
                        notify: list[str] | None = None) -> dict:
    if operator not in OPERATORS:
        return {"error": f"Invalid operator. Valid: {', '.join(sorted(OPERATORS))}"}
    return {
        "rule_id": f"rule_{secrets.token_urlsafe(8)}",
        "name": name,
        "condition": f"{metric} {OPERATORS[operator]} {threshold}",
        "metric": metric,
        "operator": operator,
        "threshold": threshold,
        "duration_sec": duration_sec,
        "notify_channels": notify or ["email"],
        "status": "active",
    }


def evaluate_rule(*, rule: dict, current_value: float) -> dict:
    op = rule["operator"]
    threshold = rule["threshold"]
    ops = {"gt": current_value > threshold, "gte": current_value >= threshold,
           "lt": current_value < threshold, "lte": current_value <= threshold,
           "eq": current_value == threshold, "ne": current_value != threshold}
    triggered = ops.get(op, False)
    return {
        "rule_id": rule.get("rule_id", ""),
        "triggered": triggered,
        "current_value": current_value,
        "threshold": threshold,
        "condition": rule.get("condition", ""),
        "severity": "critical" if triggered else "ok",
    }
