"""Platform command bus — dispatch and handle platform commands."""
from __future__ import annotations
import time

_handlers: dict[str, str] = {}
_history: list[dict] = []


def register_handler(command: str, handler: str) -> dict:
    _handlers[command] = handler
    return {"registered": True, "command": command, "handler": handler}


def dispatch(command: str, payload: dict) -> dict:
    handler = _handlers.get(command)
    if not handler:
        return {"dispatched": False, "error": "no_handler_registered"}
    entry = {"command": command, "handler": handler, "payload": payload,
             "status": "executed", "dispatched_at": time.time()}
    _history.append(entry)
    return {"dispatched": True, **entry}


def command_stats() -> dict:
    by_command: dict[str, int] = {}
    for h in _history:
        by_command[h["command"]] = by_command.get(h["command"], 0) + 1
    return {"total_dispatched": len(_history), "registered_commands": len(_handlers),
            "by_command": by_command}


def clear_bus() -> None:
    _handlers.clear()
    _history.clear()
