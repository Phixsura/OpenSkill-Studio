"""Quick action — contextual action menu builder."""

import html

DEFAULT_ACTIONS = {
    "app": [
        {"id": "edit", "label": "Edit App", "icon": "✏️", "shortcut": "E"},
        {"id": "deploy", "label": "Deploy", "icon": "🚀", "shortcut": "D"},
        {"id": "logs", "label": "View Logs", "icon": "📋", "shortcut": "L"},
        {"id": "settings", "label": "Settings", "icon": "⚙️", "shortcut": "S"},
        {"id": "delete", "label": "Delete", "icon": "🗑️", "shortcut": None, "danger": True},
    ],
    "webhook": [
        {"id": "test", "label": "Send Test", "icon": "🧪"},
        {"id": "edit", "label": "Edit", "icon": "✏️"},
        {"id": "disable", "label": "Disable", "icon": "⏸️"},
        {"id": "delete", "label": "Delete", "icon": "🗑️", "danger": True},
    ],
}


def get_actions(*, context: str, resource_id: str = "") -> dict:
    actions = DEFAULT_ACTIONS.get(context, [])
    items = [{"id": a["id"], "label": html.escape(a["label"]), "icon": a.get("icon", ""),
              "shortcut": a.get("shortcut"), "danger": a.get("danger", False)}
             for a in actions]
    return {"actions": items, "context": context, "resource_id": resource_id,
            "total": len(items)}
