"""Health Probes — Kubernetes-style liveness, readiness, and startup probes.

Implements:
- Liveness: is the process alive? (restart if not)
- Readiness: can it accept traffic? (remove from LB if not)
- Startup: has it finished initializing? (don't check liveness until ready)
- Configurable check functions per probe
- Consecutive failure threshold before reporting unhealthy
- Response format compatible with K8s probe endpoints
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class ProbeConfig:
    check_fn: callable  # () -> (bool, str)
    failure_threshold: int = 3
    success_threshold: int = 1
    period_seconds: float = 10
    timeout_seconds: float = 5
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_check: float = 0
    last_result: bool = True
    last_message: str = ""


@dataclass
class ProbeResponse:
    status: str  # "ok" or "fail"
    http_status: int  # 200 or 503
    checks: dict[str, dict] = field(default_factory=dict)
    timestamp: float = 0


class HealthProbeService:
    def __init__(self):
        self._liveness: list[tuple[str, ProbeConfig]] = []
        self._readiness: list[tuple[str, ProbeConfig]] = []
        self._startup: list[tuple[str, ProbeConfig]] = []
        self._started = False

    def add_liveness_check(self, name: str, check_fn: callable,
                           failure_threshold: int = 3) -> None:
        self._liveness.append((name, ProbeConfig(
            check_fn=check_fn, failure_threshold=failure_threshold)))

    def add_readiness_check(self, name: str, check_fn: callable,
                            failure_threshold: int = 1) -> None:
        self._readiness.append((name, ProbeConfig(
            check_fn=check_fn, failure_threshold=failure_threshold)))

    def add_startup_check(self, name: str, check_fn: callable,
                          failure_threshold: int = 10) -> None:
        self._startup.append((name, ProbeConfig(
            check_fn=check_fn, failure_threshold=failure_threshold)))

    def _run_probes(self, probes: list[tuple[str, ProbeConfig]]) -> ProbeResponse:
        checks = {}
        all_ok = True
        now = time.time()

        for name, config in probes:
            try:
                ok, message = config.check_fn()
            except Exception as e:
                ok, message = False, str(e)

            config.last_check = now
            config.last_message = message

            if ok:
                config.consecutive_failures = 0
                config.consecutive_successes += 1
                config.last_result = True
            else:
                config.consecutive_successes = 0
                config.consecutive_failures += 1
                config.last_result = False

            # Determine if this check is healthy based on thresholds
            if config.consecutive_failures >= config.failure_threshold:
                healthy = False
            elif config.consecutive_successes >= config.success_threshold:
                healthy = True
            else:
                healthy = config.last_result

            checks[name] = {"healthy": healthy, "message": message,
                            "consecutive_failures": config.consecutive_failures}
            if not healthy:
                all_ok = False

        return ProbeResponse(
            status="ok" if all_ok else "fail",
            http_status=200 if all_ok else 503,
            checks=checks, timestamp=now)

    def liveness(self) -> ProbeResponse:
        """Liveness probe: is the process alive?"""
        if not self._liveness:
            return ProbeResponse(status="ok", http_status=200, timestamp=time.time())
        return self._run_probes(self._liveness)

    def readiness(self) -> ProbeResponse:
        """Readiness probe: can it accept traffic?"""
        if not self._started and self._startup:
            return ProbeResponse(status="fail", http_status=503,
                                 checks={"startup": {"healthy": False,
                                                     "message": "Still starting up"}},
                                 timestamp=time.time())
        if not self._readiness:
            return ProbeResponse(status="ok", http_status=200, timestamp=time.time())
        return self._run_probes(self._readiness)

    def startup(self) -> ProbeResponse:
        """Startup probe: has initialization completed?"""
        if not self._startup:
            self._started = True
            return ProbeResponse(status="ok", http_status=200, timestamp=time.time())
        result = self._run_probes(self._startup)
        if result.status == "ok":
            self._started = True
        return result

    def mark_started(self) -> None:
        self._started = True

    def is_started(self) -> bool:
        return self._started

    def get_all(self) -> dict:
        return {
            "liveness": self.liveness().__dict__,
            "readiness": self.readiness().__dict__,
            "startup": self.startup().__dict__,
            "started": self._started,
        }
