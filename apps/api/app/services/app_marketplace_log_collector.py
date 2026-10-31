"""Log Collector — centralized logging for extension runtime.

Collects structured logs from sandboxed extensions, with log levels,
filtering, retention policies, and search capabilities.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import IntEnum


class LogLevel(IntEnum):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


@dataclass
class LogEntry:
    extension_id: str
    level: LogLevel
    message: str
    timestamp: str = ""
    context: dict = field(default_factory=dict)
    trace_id: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class LogCollector:
    """Collects, queries, and manages extension logs."""

    def __init__(self, max_entries_per_ext: int = 10000):
        self._logs: dict[str, list[LogEntry]] = {}
        self._max_entries = max_entries_per_ext

    def log(self, extension_id: str, level: LogLevel, message: str,
            context: dict | None = None, trace_id: str = "") -> LogEntry:
        """Record a log entry."""
        entry = LogEntry(extension_id=extension_id, level=level,
                         message=message, context=context or {}, trace_id=trace_id)
        logs = self._logs.setdefault(extension_id, [])
        logs.append(entry)
        # Enforce retention
        if len(logs) > self._max_entries:
            self._logs[extension_id] = logs[-self._max_entries:]
        return entry

    def debug(self, ext_id: str, msg: str, **ctx: object) -> LogEntry:
        return self.log(ext_id, LogLevel.DEBUG, msg, dict(ctx))

    def info(self, ext_id: str, msg: str, **ctx: object) -> LogEntry:
        return self.log(ext_id, LogLevel.INFO, msg, dict(ctx))

    def warning(self, ext_id: str, msg: str, **ctx: object) -> LogEntry:
        return self.log(ext_id, LogLevel.WARNING, msg, dict(ctx))

    def error(self, ext_id: str, msg: str, **ctx: object) -> LogEntry:
        return self.log(ext_id, LogLevel.ERROR, msg, dict(ctx))

    def critical(self, ext_id: str, msg: str, **ctx: object) -> LogEntry:
        return self.log(ext_id, LogLevel.CRITICAL, msg, dict(ctx))

    def query(self, extension_id: str, min_level: LogLevel = LogLevel.DEBUG,
              search: str = "", trace_id: str = "", limit: int = 100) -> list[LogEntry]:
        """Query logs with filters."""
        logs = self._logs.get(extension_id, [])
        results = [l for l in logs if l.level >= min_level]
        if search:
            s = search.lower()
            results = [l for l in results if s in l.message.lower()]
        if trace_id:
            results = [l for l in results if l.trace_id == trace_id]
        return results[-limit:]

    def get_error_summary(self, extension_id: str) -> dict:
        """Get summary of errors and warnings."""
        logs = self._logs.get(extension_id, [])
        by_level = {l.name: 0 for l in LogLevel}
        for entry in logs:
            by_level[LogLevel(entry.level).name] += 1
        recent_errors = [l for l in logs if l.level >= LogLevel.ERROR][-5:]
        return {
            "extension_id": extension_id,
            "total_entries": len(logs),
            "by_level": by_level,
            "recent_errors": [{"message": e.message, "timestamp": e.timestamp} for e in recent_errors],
        }

    def clear(self, extension_id: str) -> int:
        count = len(self._logs.get(extension_id, []))
        self._logs.pop(extension_id, None)
        return count
