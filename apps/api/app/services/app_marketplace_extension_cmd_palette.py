"""Extension Command Palette — quick-access command palette for the marketplace."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class PaletteCommand:
    command_id: str
    label: str
    category: str  # navigation, action, search, settings
    shortcut: str = ""
    icon: str = ""
    handler: str = ""  # route or action name


class ExtCmdPaletteService:
    def __init__(self):
        self._commands: list[PaletteCommand] = []
        self._seed()

    def _seed(self):
        defaults = [
            ("nav-home", "Go to Home", "navigation", "⌘H", "🏠", "/"),
            ("nav-ext", "Browse Extensions", "navigation", "⌘E", "🧩", "/extensions"),
            ("nav-docs", "Open Documentation", "navigation", "⌘D", "📚", "/docs"),
            ("action-new", "Create Extension", "action", "⌘N", "✨", "/new"),
            ("action-deploy", "Deploy Extension", "action", "⌘⇧D", "🚀", "/deploy"),
            ("search-ext", "Search Extensions", "search", "/", "🔍", "/search"),
            ("settings-api", "API Keys", "settings", "⌘K", "🔑", "/settings/api"),
            ("settings-profile", "Edit Profile", "settings", "", "👤", "/settings/profile"),
        ]
        for cid, label, cat, shortcut, icon, handler in defaults:
            self._commands.append(PaletteCommand(
                command_id=cid, label=label, category=cat,
                shortcut=shortcut, icon=icon, handler=handler))

    def search(self, query: str) -> list[PaletteCommand]:
        q = query.lower()
        return [c for c in self._commands if q in c.label.lower() or q in c.category.lower()]

    def get_by_category(self, category: str) -> list[PaletteCommand]:
        return [c for c in self._commands if c.category == category]

    def register(self, command_id: str, label: str, category: str,
                 shortcut: str = "", icon: str = "", handler: str = "") -> PaletteCommand:
        cmd = PaletteCommand(command_id=command_id, label=label, category=category,
                             shortcut=shortcut, icon=icon, handler=handler)
        self._commands.append(cmd)
        return cmd

    def get_all(self) -> list[PaletteCommand]:
        return list(self._commands)
