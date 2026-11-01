"""Installation status tracker — track status transitions for installations."""

from collections import defaultdict
from datetime import UTC, datetime

_transitions: dict[str, list[dict]] = defaultdict(list)

VALID_TRANSITIONS = {
    "active": {"suspended", "uninstalled"},
    "suspended": {"active", "uninstalled"},
}


def can_transition(current: str, target: str) -> bool:
    return target in VALID_TRANSITIONS.get(current, set())


def record_transition(installation_id: str, *, from_status: str, to_status: str, reason: str = "") -> dict:
    entry = {"from": from_status, "to": to_status, "reason": reason, "timestamp": datetime.now(UTC).isoformat()}
    _transitions[installation_id].append(entry)
    return entry


def get_transitions(installation_id: str) -> list[dict]:
    return _transitions.get(installation_id, [])
