"""Health pulse monitor — continuous health heartbeat for all services."""
from __future__ import annotations
import time


def collect_pulse(services: list[dict]) -> dict:
    pulses = []
    healthy = 0
    for s in services:
        ok = s.get("status") == "healthy" and s.get("latency_ms", 0) < s.get("threshold_ms", 500)
        if ok:
            healthy += 1
        pulses.append({"service": s["name"], "healthy": ok,
                        "latency_ms": s.get("latency_ms", 0)})
    total = len(pulses)
    return {"pulses": pulses, "total": total, "healthy": healthy,
            "unhealthy": total - healthy,
            "health_pct": round(healthy / max(total, 1) * 100),
            "all_healthy": healthy == total, "timestamp": time.time()}


def pulse_history(snapshots: list[dict]) -> dict:
    if len(snapshots) < 2:
        return {"trend": "insufficient"}
    recent = snapshots[-1]["health_pct"]
    prev = snapshots[-2]["health_pct"]
    return {"current": recent, "previous": prev,
            "improving": recent > prev, "stable": recent == prev,
            "snapshots": len(snapshots)}
