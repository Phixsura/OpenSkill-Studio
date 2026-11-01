"""App Uptime Monitor — track service uptime with downtime windows.

Monitors uptime for installed apps:
- Record up/down state changes
- Compute uptime percentage over period
- Track downtime windows
- Per-installation scoped monitors
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class StateChange:
    """A state change record."""

    is_up: bool
    timestamp: float = field(default_factory=time.time)
    reason: str = ""


@dataclass
class DowntimeWindow:
    """A period of downtime."""

    started_at: float
    ended_at: float | None
    duration_seconds: float
    reason: str


class AppUptimeMonitor:
    """Track service uptime with downtime windows."""

    def __init__(self) -> None:
        # (installation_id, service_id) → list[StateChange]
        self._states: dict[tuple[str, str], list[StateChange]] = {}

    def record_state(
        self,
        installation_id: str,
        service_id: str,
        is_up: bool,
        reason: str = "",
        now: float | None = None,
    ) -> StateChange:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not service_id:
            raise ValueError("service_id is required")

        change = StateChange(is_up=is_up, timestamp=now or time.time(), reason=reason)
        key = (installation_id, service_id)
        self._states.setdefault(key, []).append(change)
        return change

    def is_up(self, installation_id: str, service_id: str) -> bool:
        key = (installation_id, service_id)
        states = self._states.get(key, [])
        return states[-1].is_up if states else True

    def uptime_pct(
        self, installation_id: str, service_id: str,
        since: float | None = None, until: float | None = None,
    ) -> float:
        """Compute uptime percentage over a period."""
        key = (installation_id, service_id)
        states = self._states.get(key, [])
        if not states:
            return 100.0

        since = since or states[0].timestamp
        until = until or time.time()
        total = until - since
        if total <= 0:
            return 100.0

        up_time = 0.0
        last_ts = since
        last_up = True

        for s in states:
            if s.timestamp < since:
                last_up = s.is_up
                continue
            if s.timestamp > until:
                break
            if last_up:
                up_time += s.timestamp - last_ts
            last_ts = s.timestamp
            last_up = s.is_up

        if last_up:
            up_time += until - last_ts

        return round(up_time / total * 100, 2)

    def get_downtimes(
        self, installation_id: str, service_id: str, limit: int = 10
    ) -> list[DowntimeWindow]:
        key = (installation_id, service_id)
        states = self._states.get(key, [])
        windows: list[DowntimeWindow] = []
        down_start: float | None = None
        down_reason = ""

        for s in states:
            if not s.is_up and down_start is None:
                down_start = s.timestamp
                down_reason = s.reason
            elif s.is_up and down_start is not None:
                windows.append(DowntimeWindow(
                    started_at=down_start, ended_at=s.timestamp,
                    duration_seconds=s.timestamp - down_start,
                    reason=down_reason,
                ))
                down_start = None

        if down_start is not None:
            windows.append(DowntimeWindow(
                started_at=down_start, ended_at=None,
                duration_seconds=time.time() - down_start,
                reason=down_reason,
            ))

        return list(reversed(windows[-limit:]))

    def list_services(self, installation_id: str) -> list[str]:
        return sorted({
            sid for (inst, sid) in self._states if inst == installation_id
        })
