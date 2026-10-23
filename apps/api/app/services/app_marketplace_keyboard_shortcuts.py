"""Keyboard shortcuts — manage keyboard shortcuts for the developer console."""

SHORTCUTS = [
    {"key": "Ctrl+K", "action": "open_command_palette", "label": "Command Palette", "scope": "global"},
    {"key": "Ctrl+N", "action": "create_app", "label": "New App", "scope": "dashboard"},
    {"key": "Ctrl+S", "action": "save", "label": "Save", "scope": "editor"},
    {"key": "Ctrl+Enter", "action": "submit", "label": "Submit", "scope": "form"},
    {"key": "Ctrl+/", "action": "toggle_sidebar", "label": "Toggle Sidebar", "scope": "global"},
    {"key": "Ctrl+D", "action": "deploy", "label": "Deploy", "scope": "app_detail"},
    {"key": "Ctrl+L", "action": "view_logs", "label": "View Logs", "scope": "app_detail"},
    {"key": "Escape", "action": "close_modal", "label": "Close", "scope": "modal"},
    {"key": "?", "action": "show_shortcuts", "label": "Show Shortcuts", "scope": "global"},
]


def get_shortcuts(*, scope: str | None = None) -> list[dict]:
    if scope:
        return [s for s in SHORTCUTS if s["scope"] == scope or s["scope"] == "global"]
    return SHORTCUTS


def find_shortcut(*, key: str) -> dict | None:
    return next((s for s in SHORTCUTS if s["key"] == key), None)


def get_shortcuts_by_scope() -> dict[str, list[dict]]:
    groups: dict[str, list] = {}
    for s in SHORTCUTS:
        groups.setdefault(s["scope"], []).append(s)
    return groups
