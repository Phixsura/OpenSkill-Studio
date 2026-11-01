"""Quick Actions — registered developer shortcuts for common operations.

Provides one-click actions like deploy, rollback, restart, with
confirmation, execution tracking, and undo support.
"""
from __future__ import annotations
import secrets
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class QuickAction:
    action_id: str
    name: str
    icon: str
    command: str
    requires_confirm: bool = False
    dangerous: bool = False
    cooldown_seconds: int = 0
    execution_count: int = 0
    last_executed: float = 0.0


class ExtensionQuickActionService:
    """Registered quick actions for developer operations."""

    def __init__(self):
        self._actions: dict[str, dict[str, QuickAction]] = defaultdict(dict)

    def register(self, extension_id: str, name: str, icon: str, command: str,
                 requires_confirm: bool = False, dangerous: bool = False,
                 cooldown_seconds: int = 0) -> QuickAction:
        action_id = f"qa_{secrets.token_urlsafe(6)}"
        action = QuickAction(
            action_id=action_id, name=name, icon=icon, command=command,
            requires_confirm=requires_confirm, dangerous=dangerous,
            cooldown_seconds=cooldown_seconds,
        )
        self._actions[extension_id][action_id] = action
        return action

    def execute(self, extension_id: str, action_id: str,
                confirmed: bool = False) -> dict:
        action = self._actions.get(extension_id, {}).get(action_id)
        if not action:
            return {"ok": False, "error": "Action not found"}
        if action.requires_confirm and not confirmed:
            return {"ok": False, "error": "Confirmation required", "needs_confirm": True}
        now = time.time()
        if action.cooldown_seconds and action.last_executed:
            elapsed = now - action.last_executed
            if elapsed < action.cooldown_seconds:
                remaining = round(action.cooldown_seconds - elapsed, 1)
                return {"ok": False, "error": f"Cooldown: {remaining}s remaining"}
        action.execution_count += 1
        action.last_executed = now
        return {"ok": True, "command": action.command, "count": action.execution_count}

    def list_actions(self, extension_id: str) -> list[QuickAction]:
        return list(self._actions.get(extension_id, {}).values())

    def remove(self, extension_id: str, action_id: str) -> bool:
        return self._actions.get(extension_id, {}).pop(action_id, None) is not None
