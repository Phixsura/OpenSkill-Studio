"""Sandbox Log Router — route logs to multiple destinations with filtering.

Routes extension logs to configured destinations (console, file, webhook,
aggregator) with level filtering, format transformation, and buffering.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    FATAL = "fatal"


LEVEL_ORDER = {LogLevel.DEBUG: 0, LogLevel.INFO: 1, LogLevel.WARN: 2,
               LogLevel.ERROR: 3, LogLevel.FATAL: 4}


class DestinationType(str, Enum):
    CONSOLE = "console"
    WEBHOOK = "webhook"
    AGGREGATOR = "aggregator"
    FILE = "file"


@dataclass
class LogDestination:
    dest_id: str
    name: str
    dest_type: DestinationType
    min_level: LogLevel = LogLevel.DEBUG
    config: dict = field(default_factory=dict)
    enabled: bool = True
    routed_count: int = 0


@dataclass
class RoutedLog:
    message: str
    level: LogLevel
    destinations: list[str]  # dest_ids that received it


class SandboxLogRouterService:
    """Routes logs to multiple destinations with level filtering."""

    def __init__(self):
        self._destinations: dict[str, dict[str, LogDestination]] = defaultdict(dict)

    def add_destination(self, sandbox_id: str, dest_id: str, name: str,
                        dest_type: DestinationType,
                        min_level: LogLevel = LogLevel.DEBUG,
                        config: dict | None = None) -> LogDestination:
        if dest_id in self._destinations.get(sandbox_id, {}):
            raise ValueError(f"Destination '{dest_id}' already exists")
        dest = LogDestination(
            dest_id=dest_id, name=name, dest_type=dest_type,
            min_level=min_level, config=config or {},
        )
        self._destinations[sandbox_id][dest_id] = dest
        return dest

    def route(self, sandbox_id: str, level: LogLevel,
              message: str) -> RoutedLog:
        destinations = self._destinations.get(sandbox_id, {})
        routed_to: list[str] = []

        for dest in destinations.values():
            if not dest.enabled:
                continue
            if LEVEL_ORDER[level] < LEVEL_ORDER[dest.min_level]:
                continue
            dest.routed_count += 1
            routed_to.append(dest.dest_id)

        return RoutedLog(message=message, level=level, destinations=routed_to)

    def toggle(self, sandbox_id: str, dest_id: str) -> bool:
        dest = self._destinations.get(sandbox_id, {}).get(dest_id)
        if dest:
            dest.enabled = not dest.enabled
            return True
        return False

    def remove(self, sandbox_id: str, dest_id: str) -> bool:
        return self._destinations.get(sandbox_id, {}).pop(dest_id, None) is not None

    def list_destinations(self, sandbox_id: str) -> list[LogDestination]:
        return list(self._destinations.get(sandbox_id, {}).values())

    def get_stats(self, sandbox_id: str) -> dict:
        dests = self._destinations.get(sandbox_id, {})
        return {
            "total": len(dests),
            "enabled": sum(1 for d in dests.values() if d.enabled),
            "total_routed": sum(d.routed_count for d in dests.values()),
            "by_type": {dt.value: sum(1 for d in dests.values() if d.dest_type == dt)
                        for dt in DestinationType if any(d.dest_type == dt for d in dests.values())},
        }
