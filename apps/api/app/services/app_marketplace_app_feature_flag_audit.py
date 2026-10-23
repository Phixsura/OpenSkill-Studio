"""Feature flag audit — track all feature flag changes with history."""

import secrets
from datetime import datetime


def record_flag_change(*, flag_name: str, old_value: bool, new_value: bool,
                         changed_by: str, reason: str) -> dict:
    return {
        "audit_id": f"ffa_{secrets.token_urlsafe(8)}",
        "flag_name": flag_name,
        "old_value": old_value,
        "new_value": new_value,
        "changed_by": changed_by,
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat(),
        "change_type": "enabled" if new_value and not old_value else "disabled" if not new_value and old_value else "unchanged",
    }


def get_flag_history(*, history: list[dict], flag_name: str | None = None) -> dict:
    filtered = history if not flag_name else [h for h in history if h.get("flag_name") == flag_name]
    by_flag: dict[str, int] = {}
    for h in filtered:
        f = h.get("flag_name", "")
        by_flag[f] = by_flag.get(f, 0) + 1
    most_changed = max(by_flag, key=by_flag.get) if by_flag else None
    return {
        "entries": filtered,
        "total": len(filtered),
        "by_flag": by_flag,
        "most_changed_flag": most_changed,
    }
