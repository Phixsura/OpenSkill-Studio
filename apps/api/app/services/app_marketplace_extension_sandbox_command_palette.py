"""Sandbox Command Palette — searchable command registry for extensions.

Provides a command palette with fuzzy search, keyboard shortcut binding,
command history, categories, and conditional availability.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class Command:
    command_id: str
    title: str
    category: str
    description: str = ""
    shortcut: str = ""  # e.g. "Ctrl+Shift+P"
    handler: str = ""
    enabled: bool = True
    hidden: bool = False


class SandboxCommandPaletteService:
    """Searchable command registry with shortcuts and categories."""

    def __init__(self):
        self._commands: dict[str, dict[str, Command]] = defaultdict(dict)
        self._history: dict[str, list[str]] = defaultdict(list)

    def register(self, sandbox_id: str, command_id: str, title: str,
                 category: str, description: str = "",
                 shortcut: str = "", handler: str = "") -> Command:
        if command_id in self._commands.get(sandbox_id, {}):
            raise ValueError(f"Command '{command_id}' already registered")
        cmd = Command(
            command_id=command_id, title=title, category=category,
            description=description, shortcut=shortcut, handler=handler,
        )
        self._commands[sandbox_id][command_id] = cmd
        return cmd

    def search(self, sandbox_id: str, query: str) -> list[Command]:
        commands = self._commands.get(sandbox_id, {}).values()
        q = query.lower()
        results = []
        for cmd in commands:
            if cmd.hidden or not cmd.enabled:
                continue
            score = 0
            if q in cmd.title.lower():
                score += 10
            if q in cmd.category.lower():
                score += 5
            if q in cmd.description.lower():
                score += 3
            if q in cmd.command_id.lower():
                score += 2
            if score > 0:
                results.append((score, cmd))
        results.sort(key=lambda x: -x[0])
        return [cmd for _, cmd in results]

    def execute(self, sandbox_id: str, command_id: str) -> dict:
        cmd = self._commands.get(sandbox_id, {}).get(command_id)
        if not cmd:
            return {"ok": False, "error": "Command not found"}
        if not cmd.enabled:
            return {"ok": False, "error": "Command disabled"}

        self._history[sandbox_id].append(command_id)
        if len(self._history[sandbox_id]) > 100:
            self._history[sandbox_id] = self._history[sandbox_id][-100:]

        return {"ok": True, "handler": cmd.handler, "command": cmd.title}

    def get_by_shortcut(self, sandbox_id: str, shortcut: str) -> Command | None:
        for cmd in self._commands.get(sandbox_id, {}).values():
            if cmd.shortcut == shortcut and cmd.enabled:
                return cmd
        return None

    def get_categories(self, sandbox_id: str) -> list[str]:
        cats = {cmd.category for cmd in self._commands.get(sandbox_id, {}).values()
                if not cmd.hidden}
        return sorted(cats)

    def get_by_category(self, sandbox_id: str, category: str) -> list[Command]:
        return [cmd for cmd in self._commands.get(sandbox_id, {}).values()
                if cmd.category == category and not cmd.hidden]

    def get_recent(self, sandbox_id: str, limit: int = 10) -> list[Command]:
        recent_ids = self._history.get(sandbox_id, [])[-limit:]
        commands = self._commands.get(sandbox_id, {})
        return [commands[cid] for cid in reversed(recent_ids) if cid in commands]

    def disable(self, sandbox_id: str, command_id: str) -> bool:
        cmd = self._commands.get(sandbox_id, {}).get(command_id)
        if cmd:
            cmd.enabled = False
            return True
        return False

    def list_all(self, sandbox_id: str) -> list[Command]:
        return [cmd for cmd in self._commands.get(sandbox_id, {}).values()
                if not cmd.hidden and cmd.enabled]
