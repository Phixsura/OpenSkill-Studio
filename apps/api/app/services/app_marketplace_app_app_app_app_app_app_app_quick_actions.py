"""Platform quick actions — contextual shortcuts for common developer tasks."""
from __future__ import annotations


ACTIONS = [
    {"id": "create_app", "label": "Create App", "icon": "📱", "category": "apps", "shortcut": "⌘N"},
    {"id": "deploy", "label": "Deploy", "icon": "🚀", "category": "ops", "shortcut": "⌘⇧D"},
    {"id": "view_logs", "label": "View Logs", "icon": "📋", "category": "debug", "shortcut": "⌘L"},
    {"id": "api_explorer", "label": "API Explorer", "icon": "🧪", "category": "dev", "shortcut": "⌘E"},
    {"id": "invite_team", "label": "Invite Team", "icon": "👥", "category": "team"},
    {"id": "gen_api_key", "label": "Generate API Key", "icon": "🔑", "category": "security"},
    {"id": "add_webhook", "label": "Add Webhook", "icon": "🔗", "category": "integrations"},
    {"id": "check_status", "label": "Status Page", "icon": "🟢", "category": "ops"},
    {"id": "view_billing", "label": "Billing", "icon": "💳", "category": "account"},
    {"id": "open_docs", "label": "Documentation", "icon": "📚", "category": "help"},
]


def get_quick_actions(*, category: str | None = None, limit: int = 10) -> list[dict]:
    actions = ACTIONS
    if category:
        actions = [a for a in actions if a["category"] == category]
    return actions[:limit]


def search_actions(query: str) -> list[dict]:
    q = query.lower()
    return [a for a in ACTIONS if q in a["label"].lower() or q in a["category"].lower()]


def get_categories() -> list[str]:
    return sorted({a["category"] for a in ACTIONS})
