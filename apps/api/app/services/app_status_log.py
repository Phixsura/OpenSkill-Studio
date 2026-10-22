"""App status transition log."""
from datetime import UTC, datetime
from collections import defaultdict

_log: dict[str, list[dict]] = defaultdict(list)

def log_transition(app_id: str, from_status: str, to_status: str, actor_id: str) -> dict:
    entry = {"from": from_status, "to": to_status, "actor_id": actor_id, "timestamp": datetime.now(UTC).isoformat()}
    _log[app_id].append(entry)
    return entry

def get_transitions(app_id: str) -> list[dict]:
    return _log.get(app_id, [])
