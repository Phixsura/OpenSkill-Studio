"""Health probe — lightweight liveness and readiness checks."""
from __future__ import annotations
import time


def liveness_check() -> dict:
    return {"status": "alive", "timestamp": time.time()}


def readiness_check(dependencies: list[dict]) -> dict:
    results = []
    all_ready = True
    for dep in dependencies:
        ready = dep.get("healthy", False)
        if not ready:
            all_ready = False
        results.append({"name": dep["name"], "ready": ready,
                         "latency_ms": dep.get("latency_ms", 0)})
    return {"ready": all_ready, "dependencies": results,
            "status": "ready" if all_ready else "not_ready"}


def startup_check(*, required_env: list[str], actual_env: dict) -> dict:
    missing = [k for k in required_env if k not in actual_env]
    return {"ready": len(missing) == 0, "missing_env": missing,
            "checked": len(required_env)}
