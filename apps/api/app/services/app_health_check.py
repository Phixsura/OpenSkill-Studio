"""App Health Check Manager — monitor app endpoint health with configurable probes.

Manages health check probes for installed apps:
- Register probes per endpoint (HTTP, TCP, custom)
- Record check results (pass/fail/timeout)
- Compute availability percentage over a window
- Consecutive failure tracking for alerting
- Per-installation scoped probes
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class ProbeType(str, Enum):
    HTTP = "http"
    TCP = "tcp"
    CUSTOM = "custom"


class CheckResult(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    TIMEOUT = "timeout"


@dataclass
class ProbeConfig:
    """Configuration for a health check probe."""

    probe_id: str
    installation_id: str
    endpoint: str
    probe_type: ProbeType = ProbeType.HTTP
    interval_seconds: int = 30
    timeout_seconds: int = 5
    failure_threshold: int = 3  # consecutive failures before unhealthy


@dataclass
class CheckRecord:
    """A single check result."""

    result: CheckResult
    latency_ms: float
    timestamp: float = field(default_factory=time.time)
    message: str = ""


@dataclass
class ProbeStatus:
    """Current status of a probe."""

    probe_id: str
    endpoint: str
    healthy: bool
    consecutive_failures: int
    total_checks: int
    availability_pct: float
    last_check: CheckRecord | None
    last_failure: CheckRecord | None


class AppHealthCheckManager:
    """Manage health check probes for installed apps."""

    def __init__(self, history_limit: int = 100) -> None:
        self._probes: dict[tuple[str, str], ProbeConfig] = {}
        self._history: dict[tuple[str, str], list[CheckRecord]] = {}
        self._consecutive_failures: dict[tuple[str, str], int] = {}
        self._history_limit = max(1, history_limit)

    def register_probe(
        self,
        installation_id: str,
        probe_id: str,
        endpoint: str,
        probe_type: ProbeType = ProbeType.HTTP,
        interval_seconds: int = 30,
        timeout_seconds: int = 5,
        failure_threshold: int = 3,
    ) -> ProbeConfig:
        """Register a new health check probe."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not probe_id:
            raise ValueError("probe_id is required")
        if not endpoint:
            raise ValueError("endpoint is required")
        if interval_seconds < 1:
            raise ValueError("interval_seconds must be >= 1")
        if timeout_seconds < 1:
            raise ValueError("timeout_seconds must be >= 1")

        config = ProbeConfig(
            probe_id=probe_id,
            installation_id=installation_id,
            endpoint=endpoint,
            probe_type=probe_type,
            interval_seconds=interval_seconds,
            timeout_seconds=timeout_seconds,
            failure_threshold=failure_threshold,
        )
        key = (installation_id, probe_id)
        self._probes[key] = config
        self._history.setdefault(key, [])
        self._consecutive_failures.setdefault(key, 0)
        return config

    def record_check(
        self,
        installation_id: str,
        probe_id: str,
        result: CheckResult,
        latency_ms: float = 0.0,
        message: str = "",
        now: float | None = None,
    ) -> ProbeStatus:
        """Record a health check result."""
        key = (installation_id, probe_id)
        if key not in self._probes:
            raise KeyError(f"Probe {probe_id} not found")

        record = CheckRecord(
            result=result,
            latency_ms=max(0.0, latency_ms),
            timestamp=now or time.time(),
            message=message,
        )

        history = self._history[key]
        history.append(record)
        # Trim history
        if len(history) > self._history_limit:
            self._history[key] = history[-self._history_limit:]

        if result == CheckResult.PASS:
            self._consecutive_failures[key] = 0
        else:
            self._consecutive_failures[key] += 1

        return self.get_status(installation_id, probe_id)

    def get_status(self, installation_id: str, probe_id: str) -> ProbeStatus:
        """Get current status of a probe."""
        key = (installation_id, probe_id)
        config = self._probes.get(key)
        if config is None:
            raise KeyError(f"Probe {probe_id} not found")

        history = self._history.get(key, [])
        consec = self._consecutive_failures.get(key, 0)
        total = len(history)
        passes = sum(1 for r in history if r.result == CheckResult.PASS)
        avail = (passes / total * 100) if total > 0 else 100.0

        last_check = history[-1] if history else None
        last_failure = None
        for r in reversed(history):
            if r.result != CheckResult.PASS:
                last_failure = r
                break

        return ProbeStatus(
            probe_id=probe_id,
            endpoint=config.endpoint,
            healthy=consec < config.failure_threshold,
            consecutive_failures=consec,
            total_checks=total,
            availability_pct=round(avail, 2),
            last_check=last_check,
            last_failure=last_failure,
        )

    def remove_probe(self, installation_id: str, probe_id: str) -> None:
        """Remove a probe and its history."""
        key = (installation_id, probe_id)
        if key not in self._probes:
            raise KeyError(f"Probe {probe_id} not found")
        del self._probes[key]
        self._history.pop(key, None)
        self._consecutive_failures.pop(key, None)

    def list_probes(self, installation_id: str) -> list[ProbeConfig]:
        """List all probes for an installation."""
        return [
            config for (inst, _), config in self._probes.items()
            if inst == installation_id
        ]

    def get_availability(
        self, installation_id: str, probe_id: str, last_n: int = 0
    ) -> float:
        """Compute availability percentage, optionally over last N checks."""
        key = (installation_id, probe_id)
        if key not in self._probes:
            raise KeyError(f"Probe {probe_id} not found")
        history = self._history.get(key, [])
        if not history:
            return 100.0
        window = history[-last_n:] if last_n > 0 else history
        passes = sum(1 for r in window if r.result == CheckResult.PASS)
        return round(passes / len(window) * 100, 2)
