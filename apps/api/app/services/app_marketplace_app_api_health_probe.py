"""API health probe — deep health checks for all platform services."""

from datetime import datetime


def run_health_probes(*, services: list[dict]) -> dict:
    results = []
    for svc in services:
        checks = svc.get("checks", [])
        passed = sum(1 for c in checks if c.get("status") == "pass")
        failed = sum(1 for c in checks if c.get("status") == "fail")
        svc_healthy = failed == 0
        results.append({
            "service": svc["name"],
            "healthy": svc_healthy,
            "checks_passed": passed,
            "checks_failed": failed,
            "latency_ms": svc.get("latency_ms", 0),
            "details": checks,
        })
    all_healthy = all(r["healthy"] for r in results)
    return {
        "services": results,
        "all_healthy": all_healthy,
        "healthy_count": sum(1 for r in results if r["healthy"]),
        "total_services": len(results),
        "checked_at": datetime.utcnow().isoformat(),
        "overall_status": "healthy" if all_healthy else "degraded",
    }
