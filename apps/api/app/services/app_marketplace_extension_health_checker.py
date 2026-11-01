"""Extension Health Checker — deep health checks with dependency verification."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class HealthCheck:
    component: str
    status: str
    latency_ms: float = 0.0
    message: str = ""
    dependencies: list[str] = field(default_factory=list)
    checked_at: float = 0.0


class HealthCheckerService:
    def __init__(self):
        self._checks: dict[str, list[HealthCheck]] = {}
        self._dependencies: dict[str, list[str]] = {}

    def register(self, component: str, dependencies: list[str] | None = None) -> None:
        self._checks[component] = []
        self._dependencies[component] = dependencies or []

    def record(self, component: str, status: str, latency_ms: float = 0,
               message: str = "") -> HealthCheck:
        check = HealthCheck(component=component, status=status,
                            latency_ms=latency_ms, message=message,
                            dependencies=self._dependencies.get(component, []),
                            checked_at=time.time())
        if component not in self._checks:
            self._checks[component] = []
        self._checks[component].append(check)
        if len(self._checks[component]) > 100:
            self._checks[component] = self._checks[component][-100:]
        return check

    def get_overall(self) -> dict:
        statuses = {}
        for comp in self._checks:
            history = self._checks[comp]
            if not history:
                statuses[comp] = "unknown"
                continue
            latest = history[-1]
            deps = self._dependencies.get(comp, [])
            dep_down = any(statuses.get(d) == "down" for d in deps)
            statuses[comp] = "degraded" if dep_down else latest.status
        has_down = any(s == "down" for s in statuses.values())
        has_degraded = any(s == "degraded" for s in statuses.values())
        overall = "down" if has_down else "degraded" if has_degraded else "healthy"
        return {"overall": overall, "components": statuses}

    def get_uptime(self, component: str, window_seconds: int = 3600) -> float:
        history = self._checks.get(component, [])
        cutoff = time.time() - window_seconds
        recent = [h for h in history if h.checked_at > cutoff]
        if not recent:
            return 100.0
        healthy = sum(1 for h in recent if h.status == "healthy")
        return round(healthy / len(recent) * 100, 1)
