"""Debug console — interactive debugging tools for developers."""
from __future__ import annotations
import time
import html

_breakpoints: list[dict] = []
_console_output: list[dict] = []


def add_breakpoint(file: str, line: int, condition: str = "") -> dict:
    bp = {"id": len(_breakpoints) + 1, "file": file, "line": line,
          "condition": condition, "enabled": True, "hit_count": 0}
    _breakpoints.append(bp)
    return bp


def log_output(level: str, message: str, source: str = "") -> dict:
    entry = {"level": level, "message": html.escape(message),
             "source": source, "timestamp": time.time()}
    _console_output.append(entry)
    return entry


def get_console(limit: int = 50, level: str | None = None) -> dict:
    items = _console_output if not level else [o for o in _console_output if o["level"] == level]
    recent = list(reversed(items[-limit:]))
    by_level: dict[str, int] = {}
    for o in _console_output:
        by_level[o["level"]] = by_level.get(o["level"], 0) + 1
    return {"output": recent, "total": len(_console_output),
            "shown": len(recent), "by_level": by_level,
            "breakpoints": len(_breakpoints)}


def clear_console() -> None:
    _console_output.clear()
    _breakpoints.clear()
