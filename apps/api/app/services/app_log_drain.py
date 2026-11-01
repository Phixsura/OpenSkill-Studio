"""App Log Drain — configure log forwarding destinations.

Manages log drain configurations:
- Register log drain endpoints (HTTP, syslog)
- Filter by log level and source
- Track delivery stats (sent, failed, dropped)
- Per-installation scoped drains
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class LogDrainStats:
    """Delivery statistics for a log drain."""

    sent: int = 0
    failed: int = 0
    dropped: int = 0

    @property
    def total(self) -> int:
        return self.sent + self.failed + self.dropped

    @property
    def success_rate(self) -> float:
        if self.total == 0:
            return 100.0
        return round(self.sent / self.total * 100, 1)


@dataclass
class LogDrain:
    """A log drain configuration."""

    drain_id: str
    destination: str  # URL or syslog address
    drain_type: str  # "http", "syslog"
    min_level: str = "info"  # "debug", "info", "warn", "error"
    source_filter: str | None = None
    enabled: bool = True
    stats: LogDrainStats = field(default_factory=LogDrainStats)


LEVELS = {"debug": 0, "info": 1, "warn": 2, "error": 3}


class AppLogDrain:
    """Configure log forwarding destinations."""

    def __init__(self) -> None:
        self._drains: dict[tuple[str, str], LogDrain] = {}

    def add_drain(
        self, installation_id: str, drain_id: str, destination: str,
        drain_type: str = "http", min_level: str = "info",
        source_filter: str | None = None,
    ) -> LogDrain:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not drain_id:
            raise ValueError("drain_id is required")
        if drain_type not in ("http", "syslog"):
            raise ValueError("drain_type must be http or syslog")
        if min_level not in LEVELS:
            raise ValueError(f"min_level must be one of {list(LEVELS.keys())}")

        drain = LogDrain(
            drain_id=drain_id, destination=destination,
            drain_type=drain_type, min_level=min_level,
            source_filter=source_filter,
        )
        self._drains[(installation_id, drain_id)] = drain
        return drain

    def should_forward(
        self, installation_id: str, drain_id: str, level: str, source: str = "",
    ) -> bool:
        drain = self._get(installation_id, drain_id)
        if not drain.enabled:
            return False
        if LEVELS.get(level, 0) < LEVELS.get(drain.min_level, 0):
            return False
        if drain.source_filter and source and drain.source_filter not in source:
            return False
        return True

    def record_delivery(
        self, installation_id: str, drain_id: str, success: bool,
    ) -> LogDrainStats:
        drain = self._get(installation_id, drain_id)
        if success:
            drain.stats.sent += 1
        else:
            drain.stats.failed += 1
        return drain.stats

    def record_drop(self, installation_id: str, drain_id: str) -> LogDrainStats:
        drain = self._get(installation_id, drain_id)
        drain.stats.dropped += 1
        return drain.stats

    def toggle(self, installation_id: str, drain_id: str, enabled: bool) -> LogDrain:
        drain = self._get(installation_id, drain_id)
        drain.enabled = enabled
        return drain

    def get_stats(self, installation_id: str, drain_id: str) -> LogDrainStats:
        return self._get(installation_id, drain_id).stats

    def list_drains(self, installation_id: str) -> list[LogDrain]:
        return [d for (inst, _), d in self._drains.items() if inst == installation_id]

    def _get(self, installation_id: str, drain_id: str) -> LogDrain:
        key = (installation_id, drain_id)
        d = self._drains.get(key)
        if d is None:
            raise KeyError(f"Drain {drain_id} not found")
        return d
