"""Sandbox Log Stream — structured logging for extension sandbox execution.

Captures stdout/stderr, structures log entries with levels, supports
log search, retention policies, and real-time streaming simulation.
"""
from __future__ import annotations
import secrets
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    FATAL = "fatal"


LEVEL_SEVERITY = {LogLevel.DEBUG: 0, LogLevel.INFO: 1, LogLevel.WARN: 2,
                  LogLevel.ERROR: 3, LogLevel.FATAL: 4}


@dataclass
class LogEntry:
    entry_id: str
    sandbox_id: str
    level: LogLevel
    message: str
    source: str = "stdout"  # stdout, stderr, system
    metadata: dict = field(default_factory=dict)
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class SandboxLogStreamService:
    """Manages structured log streams for extension sandboxes."""

    MAX_ENTRIES_PER_SANDBOX = 5000

    def __init__(self):
        self._logs: dict[str, list[LogEntry]] = defaultdict(list)

    def write(self, sandbox_id: str, level: LogLevel, message: str,
              source: str = "stdout", metadata: dict | None = None) -> LogEntry:
        entry = LogEntry(
            entry_id=f"log_{secrets.token_urlsafe(6)}",
            sandbox_id=sandbox_id, level=level,
            message=message, source=source,
            metadata=metadata or {},
        )
        self._logs[sandbox_id].append(entry)
        # Enforce retention
        if len(self._logs[sandbox_id]) > self.MAX_ENTRIES_PER_SANDBOX:
            self._logs[sandbox_id] = self._logs[sandbox_id][-self.MAX_ENTRIES_PER_SANDBOX:]
        return entry

    def read(self, sandbox_id: str, limit: int = 100,
             min_level: LogLevel | None = None,
             source: str | None = None,
             search: str | None = None) -> list[LogEntry]:
        entries = self._logs.get(sandbox_id, [])
        if min_level:
            min_sev = LEVEL_SEVERITY[min_level]
            entries = [e for e in entries if LEVEL_SEVERITY[e.level] >= min_sev]
        if source:
            entries = [e for e in entries if e.source == source]
        if search:
            lower = search.lower()
            entries = [e for e in entries if lower in e.message.lower()]
        return entries[-limit:]

    def get_error_count(self, sandbox_id: str) -> int:
        return sum(1 for e in self._logs.get(sandbox_id, [])
                   if e.level in (LogLevel.ERROR, LogLevel.FATAL))

    def get_stats(self, sandbox_id: str) -> dict:
        entries = self._logs.get(sandbox_id, [])
        by_level: dict[str, int] = defaultdict(int)
        for e in entries:
            by_level[e.level.value] += 1
        return {
            "total": len(entries),
            "by_level": dict(by_level),
            "error_count": by_level.get("error", 0) + by_level.get("fatal", 0),
        }

    def clear(self, sandbox_id: str) -> int:
        count = len(self._logs.get(sandbox_id, []))
        self._logs[sandbox_id] = []
        return count

    def tail(self, sandbox_id: str, n: int = 20) -> list[LogEntry]:
        return self._logs.get(sandbox_id, [])[-n:]
