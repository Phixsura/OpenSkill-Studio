"""Scheduler — cron-like task scheduling for installed apps."""

import re

CRON_RE = re.compile(r'^(\*|[0-9,\-/]+)\s+(\*|[0-9,\-/]+)\s+(\*|[0-9,\-/]+)\s+(\*|[0-9,\-/]+)\s+(\*|[0-9,\-/]+)$')


def create_scheduled_task(*, installation_id: str, name: str, cron_expr: str,
                            action: str, config: dict | None = None) -> dict:
    if not CRON_RE.match(cron_expr):
        return {"error": f"Invalid cron expression: {cron_expr}"}
    if len(name) < 3:
        return {"error": "Name too short (min 3 chars)"}
    return {"installation_id": installation_id, "name": name, "cron_expr": cron_expr,
            "action": action, "config": config or {}, "status": "active", "error": None}


def describe_schedule(*, cron_expr: str) -> str:
    parts = cron_expr.split()
    if parts == ["*", "*", "*", "*", "*"]:
        return "Every minute"
    if parts[0] == "0" and parts[1] == "*":
        return "Every hour"
    if parts[0] == "0" and parts[1] == "0":
        return "Daily at midnight"
    if parts[4] == "1-5" and parts[0] == "0" and parts[1] == "9":
        return "Weekdays at 9:00 AM"
    return f"Cron: {cron_expr}"


def list_upcoming_runs(*, tasks: list[dict], limit: int = 10) -> list[dict]:
    active = [t for t in tasks if t.get("status") == "active"]
    return [{"name": t["name"], "cron": t["cron_expr"], "description": describe_schedule(cron_expr=t["cron_expr"])}
            for t in active[:limit]]
