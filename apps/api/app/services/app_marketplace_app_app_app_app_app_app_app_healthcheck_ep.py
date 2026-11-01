"""Health check endpoint builder — standardized health check responses."""
from __future__ import annotations
import time


def build_health_response(checks: dict[str, dict]) -> dict:
    all_healthy = True
    results = {}
    for name, check in checks.items():
        healthy = check.get("status") == "up"
        if not healthy:
            all_healthy = False
        results[name] = {"status": "up" if healthy else "down",
                          "latency_ms": check.get("latency_ms", 0),
                          "message": check.get("message", "")}
    status = "pass" if all_healthy else "fail"
    return {"status": status, "checks": results,
            "output": f"{'All systems operational' if all_healthy else 'Degraded performance'}",
            "timestamp": time.time()}


def liveness_probe() -> dict:
    return {"status": "ok", "alive": True}


def readiness_probe(dependencies: dict[str, bool]) -> dict:
    ready = all(dependencies.values())
    not_ready = [k for k, v in dependencies.items() if not v]
    return {"status": "ready" if ready else "not_ready", "ready": ready,
            "not_ready_deps": not_ready}
