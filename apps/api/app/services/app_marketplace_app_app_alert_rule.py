"""Alert rule — threshold-based alerting with notification channels."""

import html
from datetime import datetime, timezone

OPERATORS = {"gt": ">", "lt": "<", "gte": ">=", "lte": "<=", "eq": "==", "ne": "!="}


def evaluate_alert(*, metric_value: float, threshold: float,
                    operator: str = "gt") -> dict:
    ops = {"gt": lambda a, b: a > b, "lt": lambda a, b: a < b,
           "gte": lambda a, b: a >= b, "lte": lambda a, b: a <= b,
           "eq": lambda a, b: a == b, "ne": lambda a, b: a != b}
    fn = ops.get(operator)
    if not fn:
        return {"error": f"Unknown operator: {operator}"}
    triggered = fn(metric_value, threshold)
    return {"triggered": triggered, "metric_value": metric_value,
            "threshold": threshold, "operator": OPERATORS.get(operator, operator),
            "status": "firing" if triggered else "ok"}


def build_alert_rules(*, rules: list[dict]) -> dict:
    items = []
    firing = 0
    for r in rules:
        status = r.get("status", "ok")
        if status == "firing":
            firing += 1
        items.append({
            "name": html.escape(r.get("name", "")),
            "metric": r.get("metric", ""),
            "operator": OPERATORS.get(r.get("operator", "gt"), ">"),
            "threshold": r.get("threshold", 0),
            "status": status,
            "channel": r.get("channel", "email"),
            "severity": r.get("severity", "warning"),
        })
    return {"rules": items, "total": len(items), "firing": firing,
            "healthy": firing == 0}
