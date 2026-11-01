"""Health Check — define and run health check probes for extensions.

Supports liveness, readiness, and startup probes with configurable
intervals, thresholds, and failure actions.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ProbeType(str, Enum):
    LIVENESS = "liveness"
    READINESS = "readiness"
    STARTUP = "startup"


class ProbeResult(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"


@dataclass
class HealthProbe:
    probe_id: str
    extension_id: str
    probe_type: ProbeType
    endpoint: str
    interval_seconds: int = 30
    timeout_seconds: int = 5
    failure_threshold: int = 3
    success_threshold: int = 1


@dataclass
class ProbeExecution:
    probe_id: str
    result: ProbeResult
    response_ms: float = 0.0
    timestamp: str = ""
    message: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class HealthCheckService:
    """Manages and executes health check probes for extensions."""

    def __init__(self):
        self._probes: dict[str, HealthProbe] = {}
        self._history: dict[str, list[ProbeExecution]] = {}
        self._consecutive_failures: dict[str, int] = {}
        self._consecutive_successes: dict[str, int] = {}

    def register_probe(self, probe: HealthProbe) -> HealthProbe:
        self._probes[probe.probe_id] = probe
        self._consecutive_failures[probe.probe_id] = 0
        self._consecutive_successes[probe.probe_id] = 0
        return probe

    def record_execution(self, probe_id: str, result: ProbeResult,
                         response_ms: float = 0.0, message: str = "") -> dict:
        """Record a probe execution and check thresholds."""
        probe = self._probes.get(probe_id)
        if not probe:
            return {"error": "Probe not found"}

        execution = ProbeExecution(probe_id, result, response_ms, message=message)
        self._history.setdefault(probe_id, []).append(execution)

        if result == ProbeResult.SUCCESS:
            self._consecutive_failures[probe_id] = 0
            self._consecutive_successes[probe_id] = self._consecutive_successes.get(probe_id, 0) + 1
        else:
            self._consecutive_successes[probe_id] = 0
            self._consecutive_failures[probe_id] = self._consecutive_failures.get(probe_id, 0) + 1

        failed = self._consecutive_failures[probe_id] >= probe.failure_threshold
        healthy = self._consecutive_successes[probe_id] >= probe.success_threshold

        return {
            "probe_id": probe_id, "result": result.value,
            "consecutive_failures": self._consecutive_failures[probe_id],
            "consecutive_successes": self._consecutive_successes[probe_id],
            "failed_threshold": failed,
            "healthy": healthy,
        }

    def get_probe_status(self, probe_id: str) -> dict:
        probe = self._probes.get(probe_id)
        if not probe:
            return {"error": "Not found"}
        history = self._history.get(probe_id, [])
        last = history[-1] if history else None
        return {
            "probe_id": probe_id, "type": probe.probe_type.value,
            "endpoint": probe.endpoint,
            "last_result": last.result.value if last else "unknown",
            "last_response_ms": last.response_ms if last else 0,
            "consecutive_failures": self._consecutive_failures.get(probe_id, 0),
            "total_checks": len(history),
        }

    def get_extension_health(self, extension_id: str) -> dict:
        """Get health status for all probes of an extension."""
        probes = [p for p in self._probes.values() if p.extension_id == extension_id]
        statuses = [self.get_probe_status(p.probe_id) for p in probes]
        all_healthy = all(s.get("consecutive_failures", 0) == 0 for s in statuses)
        return {
            "extension_id": extension_id,
            "overall": "healthy" if all_healthy else "unhealthy",
            "probes": statuses,
        }
