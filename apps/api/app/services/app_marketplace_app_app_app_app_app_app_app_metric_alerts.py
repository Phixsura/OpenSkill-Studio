"""Metric alert rules — define and evaluate metric-based alerts."""
from __future__ import annotations


def create_alert(name: str, metric: str, operator: str, threshold: float,
                 window_min: int = 5, severity: str = "warning") -> dict:
    valid_ops = {">", "<", ">=", "<=", "==", "!="}
    if operator not in valid_ops:
        return {"created": False, "error": "invalid_operator"}
    return {"created": True, "name": name, "metric": metric, "operator": operator,
            "threshold": threshold, "window_min": window_min, "severity": severity,
            "enabled": True}


def evaluate_alert(alert: dict, current_value: float) -> dict:
    op = alert["operator"]
    t = alert["threshold"]
    ops = {">": current_value > t, "<": current_value < t, ">=": current_value >= t,
           "<=": current_value <= t, "==": current_value == t, "!=": current_value != t}
    triggered = ops.get(op, False)
    return {"name": alert["name"], "metric": alert["metric"],
            "current": current_value, "threshold": t, "operator": op,
            "triggered": triggered, "severity": alert["severity"] if triggered else None}


def evaluate_all(alerts: list[dict], values: dict[str, float]) -> dict:
    results = []
    fired = 0
    for a in alerts:
        if not a.get("enabled", True):
            continue
        val = values.get(a["metric"], 0)
        r = evaluate_alert(a, val)
        results.append(r)
        if r["triggered"]:
            fired += 1
    return {"results": results, "total": len(results), "fired": fired,
            "all_clear": fired == 0}
