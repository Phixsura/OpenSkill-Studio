"""Notification rules — configurable rules engine for developer notifications."""


def create_notification_rule(*, name: str, event_type: str, conditions: list[dict],
                                channels: list[str]) -> dict:
    valid_channels = {"email", "slack", "webhook", "in_app", "sms"}
    invalid = set(channels) - valid_channels
    if invalid:
        return {"error": f"Invalid channels: {', '.join(invalid)}"}
    return {"name": name, "event_type": event_type, "conditions": conditions,
            "channels": channels, "enabled": True, "error": None}


def evaluate_rule(*, rule: dict, event: dict) -> bool:
    if not rule.get("enabled"):
        return False
    if rule.get("event_type") != event.get("type"):
        return False
    for cond in rule.get("conditions", []):
        field = cond.get("field", "")
        op = cond.get("operator", "eq")
        value = cond.get("value")
        actual = event.get("data", {}).get(field)
        if op == "eq" and actual != value:
            return False
        elif op == "gt" and (actual is None or actual <= value):
            return False
    return True


def get_matching_rules(*, rules: list[dict], event: dict) -> list[dict]:
    return [r for r in rules if evaluate_rule(rule=r, event=event)]
