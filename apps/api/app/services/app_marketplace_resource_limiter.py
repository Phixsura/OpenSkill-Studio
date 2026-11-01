"""Resource Limiter — enforce per-extension resource limits in the sandbox.

Provides CPU, memory, disk, and network bandwidth limits with
real-time tracking and automatic enforcement actions.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class EnforcementAction(str, Enum):
    WARN = "warn"
    THROTTLE = "throttle"
    TERMINATE = "terminate"


@dataclass
class ResourceLimit:
    cpu_percent: float = 80.0
    memory_mb: float = 256.0
    disk_mb: float = 100.0
    network_mbps: float = 10.0
    max_processes: int = 10
    max_open_files: int = 100


@dataclass
class ResourceUsage:
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    disk_mb: float = 0.0
    network_mbps: float = 0.0
    processes: int = 0
    open_files: int = 0


class ResourceLimiter:
    """Enforces resource limits for sandboxed extensions."""

    def __init__(self):
        self._limits: dict[str, ResourceLimit] = {}
        self._usage: dict[str, ResourceUsage] = {}
        self._violations: list[dict] = []

    def set_limits(self, extension_id: str, limits: ResourceLimit) -> None:
        self._limits[extension_id] = limits

    def get_limits(self, extension_id: str) -> ResourceLimit:
        return self._limits.get(extension_id, ResourceLimit())

    def update_usage(self, extension_id: str, usage: ResourceUsage) -> None:
        self._usage[extension_id] = usage

    def check(self, extension_id: str) -> list[dict]:
        """Check current usage against limits. Returns list of violations."""
        limits = self.get_limits(extension_id)
        usage = self._usage.get(extension_id, ResourceUsage())
        violations = []

        checks = [
            ("cpu", usage.cpu_percent, limits.cpu_percent, "%"),
            ("memory", usage.memory_mb, limits.memory_mb, "MB"),
            ("disk", usage.disk_mb, limits.disk_mb, "MB"),
            ("network", usage.network_mbps, limits.network_mbps, "Mbps"),
            ("processes", usage.processes, limits.max_processes, ""),
            ("open_files", usage.open_files, limits.max_open_files, ""),
        ]

        for resource, current, limit, unit in checks:
            ratio = current / max(0.001, limit)
            if ratio >= 1.0:
                action = EnforcementAction.TERMINATE
            elif ratio >= 0.9:
                action = EnforcementAction.THROTTLE
            elif ratio >= 0.8:
                action = EnforcementAction.WARN
            else:
                continue

            violation = {
                "extension_id": extension_id,
                "resource": resource,
                "current": current,
                "limit": limit,
                "unit": unit,
                "ratio": round(ratio, 3),
                "action": action.value,
            }
            violations.append(violation)
            self._violations.append(violation)

        return violations

    def should_terminate(self, extension_id: str) -> bool:
        violations = self.check(extension_id)
        return any(v["action"] == EnforcementAction.TERMINATE.value for v in violations)

    def get_usage_report(self, extension_id: str) -> dict:
        limits = self.get_limits(extension_id)
        usage = self._usage.get(extension_id, ResourceUsage())
        return {
            "extension_id": extension_id,
            "cpu": {"used": usage.cpu_percent, "limit": limits.cpu_percent, "percent": round(usage.cpu_percent / max(0.001, limits.cpu_percent) * 100, 1)},
            "memory": {"used": usage.memory_mb, "limit": limits.memory_mb, "percent": round(usage.memory_mb / max(0.001, limits.memory_mb) * 100, 1)},
            "disk": {"used": usage.disk_mb, "limit": limits.disk_mb},
            "processes": {"used": usage.processes, "limit": limits.max_processes},
        }

    def get_violations(self, extension_id: str | None = None) -> list[dict]:
        if extension_id:
            return [v for v in self._violations if v["extension_id"] == extension_id]
        return list(self._violations)
