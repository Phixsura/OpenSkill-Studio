"""Execution scheduler — schedule periodic sandbox executions (cron-like)."""

from datetime import UTC, datetime

_schedules: dict[str, dict] = {}


def create_schedule(*, installation_id: str, function_name: str, cron_expression: str, enabled: bool = True) -> dict:
    schedule_id = f"sched_{installation_id}_{function_name}"
    entry = {
        "id": schedule_id, "installation_id": installation_id,
        "function_name": function_name, "cron": cron_expression,
        "enabled": enabled, "created_at": datetime.now(UTC).isoformat(),
        "last_run": None, "next_run": None, "run_count": 0,
    }
    _schedules[schedule_id] = entry
    return entry


def get_schedule(schedule_id: str) -> dict | None:
    return _schedules.get(schedule_id)


def list_schedules(installation_id: str) -> list[dict]:
    return [s for s in _schedules.values() if s["installation_id"] == installation_id]


def toggle_schedule(schedule_id: str, enabled: bool) -> bool:
    s = _schedules.get(schedule_id)
    if not s: return False
    s["enabled"] = enabled
    return True


def delete_schedule(schedule_id: str) -> bool:
    return _schedules.pop(schedule_id, None) is not None
