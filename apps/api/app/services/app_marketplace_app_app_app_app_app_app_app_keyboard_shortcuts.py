"""Keyboard shortcuts registry — manage global keyboard shortcuts."""
from __future__ import annotations

SHORTCUTS = [
    {"keys": "⌘K", "action": "open_command_palette", "label": "Command Palette", "category": "navigation"},
    {"keys": "⌘/", "action": "toggle_sidebar", "label": "Toggle Sidebar", "category": "navigation"},
    {"keys": "⌘⇧D", "action": "deploy", "label": "Deploy", "category": "actions"},
    {"keys": "⌘⇧N", "action": "new_app", "label": "New App", "category": "actions"},
    {"keys": "⌘.", "action": "open_settings", "label": "Settings", "category": "navigation"},
    {"keys": "⌘⇧L", "action": "view_logs", "label": "View Logs", "category": "debug"},
    {"keys": "?", "action": "show_shortcuts", "label": "Show Shortcuts", "category": "help"},
    {"keys": "Esc", "action": "close_modal", "label": "Close Modal", "category": "navigation"},
]


def get_shortcuts(*, category: str | None = None) -> list[dict]:
    if category:
        return [s for s in SHORTCUTS if s["category"] == category]
    return list(SHORTCUTS)


def get_by_category() -> dict[str, list[dict]]:
    cats: dict[str, list[dict]] = {}
    for s in SHORTCUTS:
        cats.setdefault(s["category"], []).append(s)
    return cats


def find_shortcut(keys: str) -> dict | None:
    return next((s for s in SHORTCUTS if s["keys"] == keys), None)
