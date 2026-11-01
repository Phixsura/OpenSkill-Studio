"""Alert rule engine — define threshold-based alerts and evaluate conditions."""
from __future__ import annotations


SEVERITY_ORDER = {"critical": 0, "warning": 1, "info": 2}


def create_rule(*, name: str, metric: str, operator: str, threshold: float,
                 severity: str = "warning", cooldown_min: int = 5) -> dict:
    if operator not in ("gt", "gte", "lt", "lte", "eq"):
        return {"error": f"Invalid operator: {operator}"}
    return {"name": name, "metric": metric, "operator": operator,
            "threshold": threshold, "severity": severity,
            "cooldown_min": cooldown_min, "enabled": True}


def evaluate_rules(rules: list[dict], metrics: dict) -> dict:
    ops = {"gt": lambda v, t: v > t, "gte": lambda v, t: v >= t,
           "lt": lambda v, t: v < t, "lte": lambda v, t: v <= t,
           "eq": lambda v, t: v == t}
    triggered = []
    for rule in rules:
        if not rule.get("enabled", True):
            continue
        metric_val = metrics.get(rule["metric"])
        if metric_val is None:
            continue
        op_fn = ops.get(rule["operator"])
        if op_fn and op_fn(metric_val, rule["threshold"]):
            triggered.append({
                "rule": rule["name"], "metric": rule["metric"],
                "value": metric_val, "threshold": rule["threshold"],
                "severity": rule["severity"],
                "message": f"{rule['metric']} is {metric_val} ({rule['operator']} {rule['threshold']})",
            })
    triggered.sort(key=lambda a: SEVERITY_ORDER.get(a["severity"], 9))
    return {"triggered": triggered, "count": len(triggered),
            "highest_severity": triggered[0]["severity"] if triggered else None}
