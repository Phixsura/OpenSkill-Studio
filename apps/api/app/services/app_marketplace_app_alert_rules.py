"""Alert rules — configurable alerts for app monitoring thresholds."""

VALID_METRICS = {"error_rate", "response_time", "cpu_usage", "memory_usage", "install_count", "api_calls"}
VALID_OPERATORS = {"gt", "lt", "gte", "lte", "eq"}


def create_alert_rule(*, app_id: str, name: str, metric: str, operator: str,
                        threshold: float, notify_channels: list[str]) -> dict:
    if metric not in VALID_METRICS:
        return {"error": f"Invalid metric. Use: {', '.join(sorted(VALID_METRICS))}"}
    if operator not in VALID_OPERATORS:
        return {"error": f"Invalid operator. Use: {', '.join(sorted(VALID_OPERATORS))}"}
    return {"app_id": app_id, "name": name, "metric": metric, "operator": operator,
            "threshold": threshold, "notify_channels": notify_channels,
            "status": "active", "error": None}


def evaluate_alert(*, rule: dict, current_value: float) -> dict:
    ops = {"gt": lambda a, b: a > b, "lt": lambda a, b: a < b,
           "gte": lambda a, b: a >= b, "lte": lambda a, b: a <= b, "eq": lambda a, b: a == b}
    op_fn = ops.get(rule["operator"], lambda a, b: False)
    triggered = op_fn(current_value, rule["threshold"])
    return {"triggered": triggered, "rule_name": rule["name"], "metric": rule["metric"],
            "current": current_value, "threshold": rule["threshold"]}


def build_alert_summary(*, alerts: list[dict]) -> dict:
    active = [a for a in alerts if a.get("triggered")]
    return {"total_rules": len(alerts), "active_alerts": len(active),
            "critical": [a for a in active if a.get("metric") in ("error_rate", "cpu_usage")]}
