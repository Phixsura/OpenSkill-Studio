"""Metric alert rule engine — evaluate metric thresholds and fire alerts."""
from __future__ import annotations


def evaluate_alert(metric: str, value: float, rules: list[dict]) -> list[dict]:
    fired = []
    for rule in rules:
        if rule["metric"] != metric:
            continue
        op = rule["operator"]
        threshold = rule["threshold"]
        triggered = False
        if op == ">" and value > threshold:
            triggered = True
        elif op == ">=" and value >= threshold:
            triggered = True
        elif op == "<" and value < threshold:
            triggered = True
        elif op == "<=" and value <= threshold:
            triggered = True
        if triggered:
            fired.append({"rule": rule["name"], "metric": metric,
                          "value": value, "threshold": threshold,
                          "severity": rule.get("severity", "warning")})
    return fired


def alert_summary(alerts: list[dict]) -> dict:
    by_severity: dict[str, int] = {}
    for a in alerts:
        sev = a.get("severity", "warning")
        by_severity[sev] = by_severity.get(sev, 0) + 1
    return {"total": len(alerts), "by_severity": by_severity,
            "has_critical": by_severity.get("critical", 0) > 0}
