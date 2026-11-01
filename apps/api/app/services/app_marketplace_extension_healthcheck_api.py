"""Health Check API — standardized health endpoint for the platform.

Returns structured health data with component status, version info,
build metadata, and dependency health for load balancers and monitors.
"""
from __future__ import annotations
import time
from dataclasses import dataclass, field


@dataclass
class ComponentHealth:
    name: str
    status: str  # healthy, degraded, down
    latency_ms: float = 0.0
    message: str = ""


class PlatformHealthCheckApiService:
    """Standardized health check endpoint."""

    VERSION = "4.0.0"
    BUILD = "4863"

    def __init__(self):
        self._components: dict[str, ComponentHealth] = {}
        self._start_time = time.time()

    def register_component(self, name: str, status: str = "healthy",
                           latency_ms: float = 0, message: str = "") -> None:
        self._components[name] = ComponentHealth(
            name=name, status=status, latency_ms=latency_ms, message=message)

    def check(self) -> dict:
        components = list(self._components.values())
        all_healthy = all(c.status == "healthy" for c in components)
        has_degraded = any(c.status == "degraded" for c in components)
        has_down = any(c.status == "down" for c in components)

        if has_down:
            overall = "down"
        elif has_degraded:
            overall = "degraded"
        elif all_healthy:
            overall = "healthy"
        else:
            overall = "unknown"

        uptime = round(time.time() - self._start_time, 1)

        return {
            "status": overall,
            "version": self.VERSION,
            "build": self.BUILD,
            "uptime_seconds": uptime,
            "timestamp": int(time.time()),
            "components": {c.name: {"status": c.status, "latency_ms": c.latency_ms,
                                    "message": c.message}
                           for c in components},
        }

    def is_healthy(self) -> bool:
        return self.check()["status"] == "healthy"

    def is_ready(self) -> bool:
        return self.check()["status"] != "down"
