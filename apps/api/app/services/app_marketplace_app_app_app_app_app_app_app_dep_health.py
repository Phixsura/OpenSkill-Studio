"""Service dependency health checker — check health of all dependencies."""
from __future__ import annotations


def check_dependencies(deps: list[dict]) -> dict:
    results = []
    for dep in deps:
        healthy = dep.get("status") == "healthy"
        latency = dep.get("latency_ms", 0)
        degraded = healthy and latency > dep.get("latency_threshold_ms", 500)
        results.append({"name": dep["name"], "healthy": healthy,
                        "degraded": degraded, "latency_ms": latency,
                        "critical": dep.get("critical", False)})
    healthy_count = sum(1 for r in results if r["healthy"] and not r["degraded"])
    degraded_count = sum(1 for r in results if r["degraded"])
    down_count = sum(1 for r in results if not r["healthy"])
    critical_down = sum(1 for r in results if not r["healthy"] and r["critical"])
    overall = "healthy" if down_count == 0 and degraded_count == 0 else (
        "critical" if critical_down > 0 else ("degraded" if degraded_count > 0 or down_count > 0 else "healthy"))
    return {"dependencies": results, "overall": overall,
            "healthy": healthy_count, "degraded": degraded_count,
            "down": down_count, "critical_down": critical_down}
