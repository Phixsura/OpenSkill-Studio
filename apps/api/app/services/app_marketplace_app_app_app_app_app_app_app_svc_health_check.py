"""Service health check orchestrator — run health checks across all services."""
from __future__ import annotations
import time


def run_health_checks(services: list[dict]) -> dict:
    results = []
    healthy = 0
    for s in services:
        checks = s.get("checks", {})
        passed = sum(1 for v in checks.values() if v)
        total = len(checks)
        ok = passed == total and total > 0
        if ok:
            healthy += 1
        results.append({"service": s["name"], "healthy": ok, "checks_passed": passed,
                         "checks_total": total, "latency_ms": s.get("latency_ms", 0)})
    overall = "healthy" if healthy == len(results) else "degraded" if healthy > len(results) * 0.5 else "outage"
    return {"results": results, "total": len(results), "healthy": healthy,
            "unhealthy": len(results) - healthy, "overall": overall,
            "health_pct": round(healthy / max(len(results), 1) * 100),
            "checked_at": time.time()}
