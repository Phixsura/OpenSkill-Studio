"""Resource Monitor — real-time resource tracking for sandboxed extensions.

Tracks CPU, memory, disk, and network usage per sandbox with threshold
alerts, usage history, and automatic throttling when limits exceeded.
"""
from __future__ import annotations
import secrets
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class AlertLevel(str, Enum):
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    THROTTLED = "throttled"


@dataclass
class ResourceSnapshot:
    timestamp: str
    cpu_percent: float
    memory_mb: float
    disk_mb: float
    network_bytes: int
    active_connections: int


@dataclass
class ResourceAlert:
    alert_id: str
    sandbox_id: str
    resource: str
    level: AlertLevel
    value: float
    threshold: float
    message: str
    timestamp: str


@dataclass
class ResourceThresholds:
    cpu_warning: float = 70.0
    cpu_critical: float = 90.0
    memory_warning: float = 80.0
    memory_critical: float = 95.0
    disk_warning: float = 75.0
    disk_critical: float = 90.0


class ResourceMonitorService:
    """Monitors sandbox resource usage with alerting and throttling."""

    def __init__(self):
        self._history: dict[str, list[ResourceSnapshot]] = defaultdict(list)
        self._thresholds: dict[str, ResourceThresholds] = {}
        self._alerts: list[ResourceAlert] = []
        self._throttled: set[str] = set()
        self._limits: dict[str, dict] = {}

    def configure(self, sandbox_id: str, limits: dict,
                  thresholds: ResourceThresholds | None = None) -> None:
        self._limits[sandbox_id] = limits
        self._thresholds[sandbox_id] = thresholds or ResourceThresholds()

    def record(self, sandbox_id: str, cpu_percent: float, memory_mb: float,
               disk_mb: float, network_bytes: int = 0,
               active_connections: int = 0) -> list[ResourceAlert]:
        snapshot = ResourceSnapshot(
            timestamp=datetime.now(timezone.utc).isoformat(),
            cpu_percent=cpu_percent, memory_mb=memory_mb,
            disk_mb=disk_mb, network_bytes=network_bytes,
            active_connections=active_connections,
        )
        self._history[sandbox_id].append(snapshot)
        # Keep last 100 snapshots
        if len(self._history[sandbox_id]) > 100:
            self._history[sandbox_id] = self._history[sandbox_id][-100:]

        return self._check_thresholds(sandbox_id, snapshot)

    def _check_thresholds(self, sandbox_id: str,
                          snap: ResourceSnapshot) -> list[ResourceAlert]:
        th = self._thresholds.get(sandbox_id, ResourceThresholds())
        limits = self._limits.get(sandbox_id, {})
        alerts: list[ResourceAlert] = []

        checks = [
            ("cpu", snap.cpu_percent, th.cpu_warning, th.cpu_critical),
            ("memory", (snap.memory_mb / max(limits.get("memory_mb", 256), 1)) * 100,
             th.memory_warning, th.memory_critical),
            ("disk", (snap.disk_mb / max(limits.get("disk_mb", 512), 1)) * 100,
             th.disk_warning, th.disk_critical),
        ]

        for resource, value, warn, crit in checks:
            if value >= crit:
                level = AlertLevel.CRITICAL
                self._throttled.add(sandbox_id)
            elif value >= warn:
                level = AlertLevel.WARNING
            else:
                continue

            alert = ResourceAlert(
                alert_id=f"ra_{secrets.token_urlsafe(8)}",
                sandbox_id=sandbox_id, resource=resource,
                level=level, value=round(value, 1), threshold=warn if level == AlertLevel.WARNING else crit,
                message=f"{resource} at {value:.1f}% ({level.value})",
                timestamp=snap.timestamp,
            )
            alerts.append(alert)
            self._alerts.append(alert)

        return alerts

    def is_throttled(self, sandbox_id: str) -> bool:
        return sandbox_id in self._throttled

    def unthrottle(self, sandbox_id: str) -> bool:
        if sandbox_id in self._throttled:
            self._throttled.discard(sandbox_id)
            return True
        return False

    def get_current(self, sandbox_id: str) -> ResourceSnapshot | None:
        history = self._history.get(sandbox_id)
        return history[-1] if history else None

    def get_history(self, sandbox_id: str, limit: int = 50) -> list[ResourceSnapshot]:
        return self._history.get(sandbox_id, [])[-limit:]

    def get_alerts(self, sandbox_id: str) -> list[ResourceAlert]:
        return [a for a in self._alerts if a.sandbox_id == sandbox_id]
