"""Audit log — immutable record of security-relevant actions."""

import secrets
from datetime import datetime


def record_action(*, actor_id: str, action: str, resource_type: str,
                    resource_id: str, ip_address: str | None = None,
                    metadata: dict | None = None) -> dict:
    return {
        "log_id": f"aud_{secrets.token_urlsafe(12)}",
        "actor_id": actor_id,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "ip_address": ip_address,
        "metadata": metadata or {},
        "timestamp": datetime.utcnow().isoformat(),
        "immutable": True,
    }


def search_audit_log(*, entries: list[dict], actor_id: str | None = None,
                       action: str | None = None, resource_type: str | None = None,
                       limit: int = 50) -> dict:
    filtered = entries
    if actor_id:
        filtered = [e for e in filtered if e.get("actor_id") == actor_id]
    if action:
        filtered = [e for e in filtered if e.get("action") == action]
    if resource_type:
        filtered = [e for e in filtered if e.get("resource_type") == resource_type]
    return {"entries": filtered[:limit], "total": len(filtered),
            "has_more": len(filtered) > limit}


def summarize_audit_log(*, entries: list[dict]) -> dict:
    actors: dict[str, int] = {}
    actions: dict[str, int] = {}
    for e in entries:
        actors[e.get("actor_id", "")] = actors.get(e.get("actor_id", ""), 0) + 1
        actions[e.get("action", "")] = actions.get(e.get("action", ""), 0) + 1
    return {
        "total_entries": len(entries),
        "unique_actors": len(actors),
        "top_actors": sorted(actors.items(), key=lambda x: x[1], reverse=True)[:5],
        "top_actions": sorted(actions.items(), key=lambda x: x[1], reverse=True)[:5],
    }
