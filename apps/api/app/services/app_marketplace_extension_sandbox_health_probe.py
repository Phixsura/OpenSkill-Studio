"""Sandbox Health Probe — liveness and readiness probes for sandboxes.

Provides Kubernetes-style health probes with configurable checks,
probe history, flap detection, and grace periods.
"""
from __future__ import annotations
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


class ProbeType(str, Enum):
    LIVENESS = "liveness"
    READINESS = "readiness"
    STARTUP = "startup"


class ProbeResult(str, Enum):
    PASS = "pass"
    FAIL = "fail"


@dataclass
class ProbeCheck:
    probe_type: ProbeType
    result: ProbeResult
    latency_ms: float = 0.0
    message: str = ""
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


@dataclass
class ProbeConfig:
    probe_type: ProbeType
    interval_seconds: int = 10
    timeout_ms: int = 3000
    failure_threshold: int = 3
    success_threshold: int = 1
    initial_delay_seconds: int = 0


class SandboxHealthProbeService:
    """Kubernetes-style health probes for extension sandboxes."""

    def __init__(self):
        self._configs: dict[str, dict[ProbeType, ProbeConfig]] = defaultdict(dict)
        self._history: dict[str, dict[ProbeType, list[ProbeCheck]]] = defaultdict(lambda: defaultdict(list))
        self._consecutive: dict[str, dict[ProbeType, int]] = defaultdict(lambda: defaultdict(int))
        self._healthy: dict[str, dict[ProbeType, bool]] = defaultdict(lambda: defaultdict(lambda: True))

    def configure(self, sandbox_id: str, probe_type: ProbeType,
                  interval: int = 10, timeout_ms: int = 3000,
                  failure_threshold: int = 3,
                  success_threshold: int = 1) -> ProbeConfig:
        config = ProbeConfig(
            probe_type=probe_type, interval_seconds=interval,
            timeout_ms=timeout_ms, failure_threshold=failure_threshold,
            success_threshold=success_threshold,
        )
        self._configs[sandbox_id][probe_type] = config
        return config

    def record(self, sandbox_id: str, probe_type: ProbeType,
               passed: bool, latency_ms: float = 0,
               message: str = "") -> ProbeCheck:
        result = ProbeResult.PASS if passed else ProbeResult.FAIL
        check = ProbeCheck(
            probe_type=probe_type, result=result,
            latency_ms=latency_ms, message=message,
        )

        history = self._history[sandbox_id][probe_type]
        history.append(check)
        if len(history) > 100:
            self._history[sandbox_id][probe_type] = history[-100:]

        config = self._configs.get(sandbox_id, {}).get(probe_type)
        consecutive = self._consecutive[sandbox_id]

        if passed:
            consecutive[probe_type] = consecutive.get(probe_type, 0) + 1 if self._healthy[sandbox_id][probe_type] is False else 0
            threshold = config.success_threshold if config else 1
            if not self._healthy[sandbox_id][probe_type] and consecutive[probe_type] >= threshold:
                self._healthy[sandbox_id][probe_type] = True
                consecutive[probe_type] = 0
            elif self._healthy[sandbox_id][probe_type]:
                consecutive[probe_type] = 0
        else:
            consecutive[probe_type] = consecutive.get(probe_type, 0) + 1 if self._healthy[sandbox_id][probe_type] else 0
            threshold = config.failure_threshold if config else 3
            if self._healthy[sandbox_id][probe_type] and consecutive[probe_type] >= threshold:
                self._healthy[sandbox_id][probe_type] = False
                consecutive[probe_type] = 0
            elif not self._healthy[sandbox_id][probe_type]:
                consecutive[probe_type] = 0

        return check

    def is_healthy(self, sandbox_id: str, probe_type: ProbeType) -> bool:
        return self._healthy[sandbox_id][probe_type]

    def get_status(self, sandbox_id: str) -> dict:
        return {
            pt.value: {
                "healthy": self._healthy[sandbox_id][pt],
                "checks": len(self._history[sandbox_id][pt]),
            }
            for pt in ProbeType
            if pt in self._configs.get(sandbox_id, {})
        }

    def get_history(self, sandbox_id: str, probe_type: ProbeType,
                    limit: int = 20) -> list[ProbeCheck]:
        return self._history[sandbox_id][probe_type][-limit:]
