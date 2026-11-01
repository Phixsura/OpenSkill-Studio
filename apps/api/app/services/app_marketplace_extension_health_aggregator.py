"""Health Check Aggregator — dependency-aware health with SLA tracking.

Implements:
- Component health checks with configurable intervals
- Dependency graph: if a dependency is unhealthy, dependents degrade
- SLA tracking: uptime percentage over rolling windows
- Flap detection: rapid healthy↔unhealthy transitions
- Alert thresholds and incident creation
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
from collections import deque


@dataclass
class HealthRecord:
    timestamp: float
    healthy: bool
    latency_ms: float = 0
    message: str = ""


@dataclass
class Component:
    name: str
    dependencies: list[str] = field(default_factory=list)
    history: deque = field(default_factory=lambda: deque(maxlen=1000))
    healthy: bool = True
    flap_count: int = 0
    last_status_change: float = 0
    check_interval_s: float = 30


class HealthAggregatorService:
    FLAP_WINDOW_S = 300  # 5 minutes
    FLAP_THRESHOLD = 5   # status changes in window = flapping

    def __init__(self):
        self._components: dict[str, Component] = {}

    def register(self, name: str, dependencies: list[str] | None = None,
                 check_interval: float = 30) -> Component:
        comp = Component(name=name, dependencies=dependencies or [],
                         check_interval_s=check_interval)
        self._components[name] = comp
        return comp

    def record(self, name: str, healthy: bool, latency_ms: float = 0,
               message: str = "") -> dict:
        """Record a health check result. Returns derived status."""
        comp = self._components.get(name)
        if not comp:
            return {"error": "Component not registered"}

        now = time.time()
        record = HealthRecord(timestamp=now, healthy=healthy,
                              latency_ms=latency_ms, message=message)
        comp.history.append(record)

        # Detect status change → flap tracking
        if comp.healthy != healthy:
            comp.flap_count += 1
            comp.last_status_change = now
            comp.healthy = healthy

        # Decay old flaps
        if comp.last_status_change and (now - comp.last_status_change) > self.FLAP_WINDOW_S:
            comp.flap_count = max(0, comp.flap_count - 1)

        flapping = comp.flap_count >= self.FLAP_THRESHOLD

        return {
            "component": name,
            "healthy": healthy,
            "derived_status": self._derive_status(name),
            "flapping": flapping,
            "latency_ms": latency_ms,
        }

    def _derive_status(self, name: str) -> str:
        """Derive status considering dependencies."""
        comp = self._components.get(name)
        if not comp:
            return "unknown"

        if not comp.healthy:
            return "down"

        # Check dependencies
        for dep_name in comp.dependencies:
            dep = self._components.get(dep_name)
            if dep and not dep.healthy:
                return "degraded"  # dependency down → we're degraded

        return "healthy"

    def get_overall(self) -> dict:
        """Aggregate health across all components."""
        statuses = {}
        for name in self._components:
            statuses[name] = self._derive_status(name)

        has_down = any(s == "down" for s in statuses.values())
        has_degraded = any(s == "degraded" for s in statuses.values())
        overall = "down" if has_down else "degraded" if has_degraded else "healthy"

        return {"overall": overall, "components": statuses}

    def get_uptime(self, name: str, window_s: float = 3600) -> float:
        """Calculate uptime percentage over a time window."""
        comp = self._components.get(name)
        if not comp or not comp.history:
            return 100.0

        now = time.time()
        cutoff = now - window_s
        recent = [r for r in comp.history if r.timestamp > cutoff]
        if not recent:
            return 100.0

        healthy_count = sum(1 for r in recent if r.healthy)
        return round(healthy_count / len(recent) * 100, 2)

    def get_latency_stats(self, name: str, window_s: float = 3600) -> dict:
        """Get latency statistics for a component."""
        comp = self._components.get(name)
        if not comp:
            return {}

        now = time.time()
        latencies = [r.latency_ms for r in comp.history
                     if r.timestamp > now - window_s and r.latency_ms > 0]
        if not latencies:
            return {"count": 0}

        sorted_l = sorted(latencies)
        return {
            "count": len(latencies),
            "avg": round(sum(latencies) / len(latencies), 1),
            "p50": sorted_l[len(sorted_l) // 2],
            "p99": sorted_l[int(len(sorted_l) * 0.99)],
            "max": sorted_l[-1],
        }

    def get_incidents(self) -> list[dict]:
        """Find components that are currently down or flapping."""
        incidents = []
        for name, comp in self._components.items():
            status = self._derive_status(name)
            if status != "healthy":
                incidents.append({
                    "component": name, "status": status,
                    "flapping": comp.flap_count >= self.FLAP_THRESHOLD,
                    "message": comp.history[-1].message if comp.history else ""})
        return incidents
