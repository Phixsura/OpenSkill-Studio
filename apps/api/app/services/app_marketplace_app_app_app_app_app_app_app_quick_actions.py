"""Quick action launcher — frequently used platform operations."""
from __future__ import annotations

ACTIONS = [
    {"id": "deploy", "label": "Deploy to Production", "icon": "🚀", "category": "deployment", "shortcut": "⌘+D"},
    {"id": "rollback", "label": "Rollback Last Deploy", "icon": "⏪", "category": "deployment", "shortcut": "⌘+R"},
    {"id": "scale", "label": "Scale Service", "icon": "📈", "category": "infrastructure", "shortcut": "⌘+S"},
    {"id": "incident", "label": "Declare Incident", "icon": "🚨", "category": "operations", "shortcut": "⌘+I"},
    {"id": "freeze", "label": "Deploy Freeze", "icon": "🧊", "category": "deployment", "shortcut": "⌘+F"},
    {"id": "runbook", "label": "Run Runbook", "icon": "📋", "category": "operations", "shortcut": "⌘+B"},
]


def list_actions(category: str | None = None) -> dict:
    items = ACTIONS if not category else [a for a in ACTIONS if a["category"] == category]
    categories = sorted({a["category"] for a in ACTIONS})
    return {"actions": items, "total": len(items), "categories": categories}


def execute_action(action_id: str) -> dict:
    action = next((a for a in ACTIONS if a["id"] == action_id), None)
    if not action:
        return {"executed": False, "error": "unknown_action"}
    return {"executed": True, "action": action["label"], "category": action["category"]}
