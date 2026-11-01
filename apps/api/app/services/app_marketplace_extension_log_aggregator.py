"""Extension Log Aggregator — centralized logging for extensions."""
from __future__ import annotations
from dataclasses import dataclass
import time
from collections import deque


@dataclass
class LogEntry:
    log_id: str
    extension_id: str
    level: str  # debug, info, warn, error, fatal
    message: str
    metadata: dict | None = None
    timestamp: float = 0.0
    def __post_init__(self):
        if not self.timestamp: self.timestamp = time.time()


class ExtLogAggregatorService:
    LEVELS = {"debug": 0, "info": 1, "warn": 2, "error": 3, "fatal": 4}
    MAX_LOGS = 10000

    def __init__(self):
        self._logs: deque[LogEntry] = deque(maxlen=self.MAX_LOGS)
        self._counter = 0

    def log(self, extension_id: str, level: str, message: str,
            metadata: dict | None = None) -> LogEntry:
        if level not in self.LEVELS:
            level = "info"
        self._counter += 1
        entry = LogEntry(log_id=f"log-{self._counter}", extension_id=extension_id,
                         level=level, message=message, metadata=metadata)
        self._logs.append(entry)
        return entry

    def query(self, extension_id: str | None = None, level: str | None = None,
              min_level: str | None = None, limit: int = 100,
              search: str | None = None) -> list[LogEntry]:
        results = list(reversed(self._logs))
        if extension_id:
            results = [l for l in results if l.extension_id == extension_id]
        if level:
            results = [l for l in results if l.level == level]
        if min_level and min_level in self.LEVELS:
            threshold = self.LEVELS[min_level]
            results = [l for l in results if self.LEVELS.get(l.level, 0) >= threshold]
        if search:
            s = search.lower()
            results = [l for l in results if s in l.message.lower()]
        return results[:limit]

    def get_counts(self, extension_id: str) -> dict[str, int]:
        counts = {k: 0 for k in self.LEVELS}
        for l in self._logs:
            if l.extension_id == extension_id:
                counts[l.level] = counts.get(l.level, 0) + 1
        return counts
