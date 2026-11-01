"""App API Uptime Monitor — track API uptime over time windows.

Manages uptime monitoring:
- Record up/down checks
- Calculate uptime percentage per window
- Track consecutive downtime
- Per-installation scoped monitors
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class UptimeCheck:
    """A single uptime check result."""

    up: bool
    timestamp: float = field(default_factory=time.time)


@dataclass
class UptimeMonitor:
    """An uptime monitor for a service."""

    monitor_id: str
    service_name: str
    checks: list[UptimeCheck] = field(default_factory=list)
    consecutive_down: int = 0

    @property
    def uptime_pct(self) -> float:
        if not self.checks:
            return 100.0
        up = sum(1 for c in self.checks if c.up)
        return round(up / len(self.checks) * 100, 2)

    @property
    def total_checks(self) -> int:
        return len(self.checks)


class AppAPIUptimeMonitor:
    """Track API uptime over time windows."""

    def __init__(self, max_checks: int = 1000) -> None:
        self._max = max(1, max_checks)
        self._monitors: dict[tuple[str, str], UptimeMonitor] = {}

    def register(self, installation_id: str, monitor_id: str, service_name: str) -> UptimeMonitor:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, monitor_id)
        if key in self._monitors:
            raise ValueError(f"Monitor {monitor_id} already exists")
        m = UptimeMonitor(monitor_id=monitor_id, service_name=service_name)
        self._monitors[key] = m
        return m

    def record_check(self, installation_id: str, monitor_id: str, up: bool) -> UptimeMonitor:
        m = self._get(installation_id, monitor_id)
        m.checks.append(UptimeCheck(up=up))
        if len(m.checks) > self._max:
            m.checks = m.checks[-self._max:]
        if up:
            m.consecutive_down = 0
        else:
            m.consecutive_down += 1
        return m

    def get_monitor(self, installation_id: str, monitor_id: str) -> UptimeMonitor:
        return self._get(installation_id, monitor_id)

    def down_monitors(self, installation_id: str) -> list[UptimeMonitor]:
        return [
            m for (inst, _), m in self._monitors.items()
            if inst == installation_id and m.consecutive_down > 0
        ]

    def list_monitors(self, installation_id: str) -> list[UptimeMonitor]:
        return [m for (inst, _), m in self._monitors.items() if inst == installation_id]

    def _get(self, installation_id: str, monitor_id: str) -> UptimeMonitor:
        key = (installation_id, monitor_id)
        m = self._monitors.get(key)
        if m is None:
            raise KeyError(f"Monitor {monitor_id} not found")
        return m
