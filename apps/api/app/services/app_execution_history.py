"""Execution history — queryable execution history."""

from collections import defaultdict

_history: dict[str, list[dict]] = defaultdict(list)


def record_execution(*, app_id: str, function_name: str, success: bool, duration_ms: int,
                      trigger: str = "event", error: str | None = None) -> dict:
    from datetime import UTC, datetime
    entry = {"function_name": function_name, "success": success, "duration_ms": duration_ms,
             "trigger": trigger, "error": error, "timestamp": datetime.now(UTC).isoformat()}
    _history[app_id].append(entry)
    if len(_history[app_id]) > 5000:
        _history[app_id] = _history[app_id][-2500:]
    return entry


def query_history(app_id: str, *, function_name: str | None = None, success: bool | None = None, limit: int = 50) -> list[dict]:
    entries = _history.get(app_id, [])
    if function_name:
        entries = [e for e in entries if e["function_name"] == function_name]
    if success is not None:
        entries = [e for e in entries if e["success"] == success]
    return entries[-limit:]
