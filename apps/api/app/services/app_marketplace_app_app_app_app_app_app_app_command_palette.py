"""Command palette — searchable command registry for keyboard-driven navigation."""
from __future__ import annotations


class CommandPalette:
    def __init__(self):
        self._commands: list[dict] = []

    def register(self, *, id: str, title: str, shortcut: str = "",
                  category: str = "general", action: str = "navigate",
                  url: str = "", icon: str = "📌") -> dict:
        cmd = {"id": id, "title": title, "shortcut": shortcut,
               "category": category, "action": action, "url": url, "icon": icon}
        self._commands.append(cmd)
        return {"registered": id}

    def search(self, query: str, *, limit: int = 10) -> list[dict]:
        q = query.lower()
        scored = []
        for cmd in self._commands:
            title_lower = cmd["title"].lower()
            if q in title_lower:
                score = 10 if title_lower.startswith(q) else 5
                scored.append({**cmd, "score": score})
            elif q in cmd["category"].lower():
                scored.append({**cmd, "score": 2})
        scored.sort(key=lambda c: -c["score"])
        return scored[:limit]

    def by_category(self) -> dict[str, list[dict]]:
        cats: dict[str, list[dict]] = {}
        for cmd in self._commands:
            cats.setdefault(cmd["category"], []).append(cmd)
        return cats

    def list_all(self) -> list[dict]:
        return list(self._commands)
