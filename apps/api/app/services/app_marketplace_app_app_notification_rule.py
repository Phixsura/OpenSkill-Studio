"""Notification rule — configurable rules for triggering notifications."""


RULE_TYPES = {
    "threshold": {"label": "Threshold Alert", "icon": "📊"},
    "anomaly": {"label": "Anomaly Detection", "icon": "🔍"},
    "schedule": {"label": "Scheduled Check", "icon": "⏰"},
    "event": {"label": "Event Trigger", "icon": "⚡"},
}

CHANNELS = {"email", "slack", "push", "webhook", "sms"}


def create_notification_rule(*, name: str, rule_type: str, condition: dict,
                                channels: list[str], enabled: bool = True) -> dict:
    if rule_type not in RULE_TYPES:
        return {"error": f"Invalid type. Valid: {', '.join(sorted(RULE_TYPES))}"}
    invalid_channels = set(channels) - CHANNELS
    if invalid_channels:
        return {"error": f"Invalid channels: {', '.join(sorted(invalid_channels))}"}
    return {
        "name": name,
        "rule_type": rule_type,
        "type_info": RULE_TYPES[rule_type],
        "condition": condition,
        "channels": sorted(channels),
        "enabled": enabled,
    }


def evaluate_rules(*, rules: list[dict], metrics: dict) -> dict:
    triggered = []
    for rule in rules:
        if not rule.get("enabled"):
            continue
        condition = rule.get("condition", {})
        metric_name = condition.get("metric")
        operator = condition.get("operator", "gt")
        threshold = condition.get("threshold", 0)
        current = metrics.get(metric_name, 0)
        ops = {"gt": current > threshold, "lt": current < threshold,
               "gte": current >= threshold, "lte": current <= threshold}
        if ops.get(operator, False):
            triggered.append({"rule": rule["name"], "metric": metric_name,
                              "current": current, "threshold": threshold})
    return {"triggered": triggered, "triggered_count": len(triggered),
            "total_rules": len(rules)}
