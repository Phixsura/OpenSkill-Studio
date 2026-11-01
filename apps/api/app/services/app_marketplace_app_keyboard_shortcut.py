"""Keyboard shortcut — manage keyboard shortcuts for the platform."""


DEFAULT_SHORTCUTS = [
    {"key": "Cmd+K", "action": "search", "label": "Open Search", "category": "navigation"},
    {"key": "Cmd+N", "action": "new_app", "label": "New App", "category": "actions"},
    {"key": "Cmd+D", "action": "deploy", "label": "Deploy", "category": "actions"},
    {"key": "Cmd+,", "action": "settings", "label": "Settings", "category": "navigation"},
    {"key": "Cmd+/", "action": "help", "label": "Help", "category": "help"},
    {"key": "Cmd+Shift+L", "action": "logs", "label": "View Logs", "category": "debug"},
    {"key": "Escape", "action": "close_modal", "label": "Close Modal", "category": "navigation"},
]


def get_shortcuts(*, category: str | None = None) -> dict:
    filtered = DEFAULT_SHORTCUTS
    if category:
        filtered = [s for s in filtered if s["category"] == category]
    categories = sorted(set(s["category"] for s in DEFAULT_SHORTCUTS))
    return {"shortcuts": filtered, "total": len(filtered), "categories": categories}


def find_shortcut(*, key: str) -> dict:
    match = next((s for s in DEFAULT_SHORTCUTS if s["key"].lower() == key.lower()), None)
    if not match:
        return {"found": False, "key": key}
    return {"found": True, **match}
