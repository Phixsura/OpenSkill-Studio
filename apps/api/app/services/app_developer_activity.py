"""Developer activity tracker — track recent developer actions."""

from collections import defaultdict
from datetime import UTC, datetime

_activity: dict[str, list[dict]] = defaultdict(list)


def record_activity(*, developer_id: str, action: str, resource: str, details: str = "") -> dict:
    entry = {"action": action, "resource": resource, "details": details,
             "timestamp": datetime.now(UTC).isoformat()}
    _activity[developer_id].append(entry)
    if len(_activity[developer_id]) > 200:
        _activity[developer_id] = _activity[developer_id][-100:]
    return entry


def get_recent_activity(developer_id: str, *, limit: int = 20) -> list[dict]:
    return _activity.get(developer_id, [])[-limit:]


def get_activity_stats(developer_id: str) -> dict:
    entries = _activity.get(developer_id, [])
    actions: dict[str, int] = defaultdict(int)
    for e in entries:
        actions[e["action"]] += 1
    return {"total": len(entries), "by_action": dict(actions)}
