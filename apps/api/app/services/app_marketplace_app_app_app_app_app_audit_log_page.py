"""Audit log page — comprehensive audit log with filters and export."""

import html
from collections import defaultdict
from datetime import datetime, timezone

ACTIONS = {
    "create_app": "📦", "update_app": "✏️", "delete_app": "🗑️", "deploy": "🚀",
    "login": "🔑", "logout": "👋", "invite_member": "👤", "remove_member": "❌",
    "create_webhook": "🔗", "generate_key": "🔐", "change_plan": "💳",
}


def build_audit_log_page(*, events: list[dict], filter_action: str | None = None,
                            filter_actor: str | None = None, page: int = 1,
                            page_size: int = 25) -> dict:
    filtered = events
    if filter_action:
        filtered = [e for e in filtered if e.get("action") == filter_action]
    if filter_actor:
        filtered = [e for e in filtered if e.get("actor") == filter_actor]
    total = len(filtered)
    start = (page - 1) * page_size
    page_items = filtered[start:start + page_size]
    items = [{
        "action": e.get("action", ""),
        "icon": ACTIONS.get(e.get("action", ""), "📌"),
        "actor": html.escape(e.get("actor", "")),
        "target": html.escape(e.get("target", "")),
        "ip": e.get("ip", ""),
        "timestamp": e.get("timestamp", ""),
    } for e in page_items]
    actors = sorted(set(e.get("actor", "") for e in events))
    actions = sorted(set(e.get("action", "") for e in events))
    return {"events": items, "total": total, "page": page,
            "total_pages": max(1, -(-total // page_size)),
            "available_actions": actions, "available_actors": actors}
