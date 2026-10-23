"""Webhook routing engine — route events to multiple endpoints with priority."""

from datetime import datetime, timezone


def create_routing_rule(*, event_type: str, endpoint_url: str, priority: int = 0,
                          filter_expression: str | None = None) -> dict:
    if priority < 0 or priority > 100:
        return {"error": "Priority must be 0-100"}
    return {"event_type": event_type, "endpoint_url": endpoint_url, "priority": priority,
            "filter_expression": filter_expression, "active": True, "error": None}


def route_event(*, event_type: str, rules: list[dict]) -> list[dict]:
    matching = [r for r in rules if r.get("event_type") == event_type and r.get("active")]
    return sorted(matching, key=lambda r: -r.get("priority", 0))


def build_routing_table(*, rules: list[dict]) -> dict:
    table: dict[str, list] = {}
    for r in rules:
        et = r.get("event_type", "")
        table.setdefault(et, []).append({"url": r["endpoint_url"], "priority": r.get("priority", 0)})
    return {"event_types": list(table.keys()), "routes": table, "total_rules": len(rules)}
