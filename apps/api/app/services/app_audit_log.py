"""App audit log service — tracks developer platform actions.

Records all significant actions for compliance and debugging:
- App lifecycle transitions
- Installation/uninstall events
- API key creation/revocation
- Secret access
- Review decisions
- Configuration changes
"""

import structlog
from datetime import UTC, datetime
from collections import defaultdict

log = structlog.get_logger()

# In-memory audit log (production would use DB)
_audit_entries: list[dict] = []


def record_audit_event(
    *,
    actor_id: str,
    actor_type: str = "user",  # user, system, app
    action: str,
    resource_type: str,
    resource_id: str,
    details: dict | None = None,
    org_id: str | None = None,
    app_id: str | None = None,
) -> dict:
    """Record an audit log entry."""
    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "actor_id": actor_id,
        "actor_type": actor_type,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "details": details or {},
        "org_id": org_id,
        "app_id": app_id,
    }
    _audit_entries.append(entry)
    log.info("audit_event", **{k: v for k, v in entry.items() if v is not None})
    return entry


def get_audit_log(
    *,
    resource_type: str | None = None,
    resource_id: str | None = None,
    actor_id: str | None = None,
    app_id: str | None = None,
    action: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """Query audit log entries with filters."""
    results = _audit_entries
    if resource_type:
        results = [e for e in results if e["resource_type"] == resource_type]
    if resource_id:
        results = [e for e in results if e["resource_id"] == resource_id]
    if actor_id:
        results = [e for e in results if e["actor_id"] == actor_id]
    if app_id:
        results = [e for e in results if e["app_id"] == app_id]
    if action:
        results = [e for e in results if e["action"] == action]
    return results[-limit:]


def get_audit_summary(app_id: str) -> dict:
    """Get a summary of audit events for an app."""
    entries = [e for e in _audit_entries if e["app_id"] == app_id]
    action_counts: dict[str, int] = defaultdict(int)
    for e in entries:
        action_counts[e["action"]] += 1
    return {
        "app_id": app_id,
        "total_events": len(entries),
        "action_counts": dict(action_counts),
        "first_event": entries[0]["timestamp"] if entries else None,
        "last_event": entries[-1]["timestamp"] if entries else None,
    }


def clear_audit_log() -> int:
    """Clear all audit entries (testing only)."""
    count = len(_audit_entries)
    _audit_entries.clear()
    return count
