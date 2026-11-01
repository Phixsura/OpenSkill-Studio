"""Scheduled task — manage cron-like recurring tasks for apps."""

import re
import secrets
from datetime import datetime


CRON_FIELD_RE = re.compile(r"^(\*|[0-9]{1,2}(-[0-9]{1,2})?)(\/[0-9]{1,2})?$")


def validate_cron(*, expression: str) -> dict:
    fields = expression.strip().split()
    if len(fields) != 5:
        return {"valid": False, "errors": ["Cron expression must have 5 fields"]}
    errors = []
    labels = ["minute", "hour", "day_of_month", "month", "day_of_week"]
    for i, (field, label) in enumerate(zip(fields, labels)):
        parts = field.split(",")
        for part in parts:
            if not CRON_FIELD_RE.match(part):
                errors.append(f"Invalid {label}: {part}")
    return {"valid": len(errors) == 0, "errors": errors, "expression": expression}


def create_scheduled_task(*, app_id: str, name: str, cron: str,
                            endpoint: str, method: str = "POST") -> dict:
    validation = validate_cron(expression=cron)
    if not validation["valid"]:
        return {"error": validation["errors"][0]}
    task_id = f"task_{secrets.token_urlsafe(8)}"
    return {
        "task_id": task_id,
        "app_id": app_id,
        "name": name,
        "cron": cron,
        "endpoint": endpoint,
        "method": method,
        "status": "active",
        "created_at": datetime.utcnow().isoformat(),
        "next_run": None,
    }


def list_scheduled_tasks(*, app_id: str) -> dict:
    return {
        "app_id": app_id,
        "tasks": [
            {"task_id": "t1", "name": "Daily cleanup", "cron": "0 3 * * *", "status": "active",
             "last_run": "2026-10-23T03:00:00", "success_count": 42, "fail_count": 1},
            {"task_id": "t2", "name": "Hourly sync", "cron": "0 * * * *", "status": "paused",
             "last_run": "2026-10-22T18:00:00", "success_count": 100, "fail_count": 0},
        ],
        "total": 2,
    }
