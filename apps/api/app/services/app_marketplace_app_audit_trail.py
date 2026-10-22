"""Audit trail — immutable log of all app lifecycle events."""

from datetime import datetime, timezone


AUDIT_ACTIONS = {
    "app.created", "app.published", "app.suspended", "app.deleted",
    "version.submitted", "version.approved", "version.rejected",
    "install.created", "install.removed",
    "config.changed", "secret.rotated", "key.created", "key.revoked",
    "team.member_added", "team.member_removed", "team.role_changed",
    "transfer.initiated", "transfer.completed",
}


def create_audit_entry(*, app_id: str, action: str, actor_id: str,
                         details: dict | None = None, ip_address: str | None = None) -> dict:
    if action not in AUDIT_ACTIONS:
        return {"error": f"Unknown action: {action}"}
    return {
        "app_id": app_id, "action": action, "actor_id": actor_id,
        "details": details or {}, "ip_address": ip_address,
        "timestamp": datetime.now(timezone.utc).isoformat(), "error": None,
    }


def query_audit_trail(*, entries: list[dict], action_filter: str | None = None,
                        actor_filter: str | None = None, limit: int = 50) -> dict:
    result = entries
    if action_filter:
        result = [e for e in result if e.get("action") == action_filter]
    if actor_filter:
        result = [e for e in result if e.get("actor_id") == actor_filter]
    result = sorted(result, key=lambda e: e.get("timestamp", ""), reverse=True)[:limit]
    return {"entries": result, "total": len(entries), "filtered": len(result)}


def summarize_audit(*, entries: list[dict]) -> dict:
    actors = set()
    action_counts: dict[str, int] = {}
    for e in entries:
        actors.add(e.get("actor_id"))
        a = e.get("action", "unknown")
        action_counts[a] = action_counts.get(a, 0) + 1
    top_actions = sorted(action_counts.items(), key=lambda x: -x[1])[:5]
    return {
        "total_events": len(entries), "unique_actors": len(actors),
        "top_actions": [{"action": a, "count": c} for a, c in top_actions],
    }
