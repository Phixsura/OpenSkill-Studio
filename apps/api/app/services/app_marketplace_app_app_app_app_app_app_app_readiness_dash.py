"""Service readiness dashboard — unified production readiness view."""
from __future__ import annotations


def readiness_dashboard(services: list[dict]) -> dict:
    results = []
    for s in services:
        checks = {
            "health_check": s.get("health_check", False),
            "monitoring": s.get("monitoring", False),
            "logging": s.get("logging", False),
            "alerting": s.get("alerting", False),
            "runbooks": s.get("runbooks", False),
            "load_tested": s.get("load_tested", False),
        }
        score = sum(1 for v in checks.values() if v)
        total = len(checks)
        ready = score == total
        results.append({"service": s["name"], "score": score, "total": total,
                        "ready": ready, "checks": checks})
    ready_count = sum(1 for r in results if r["ready"])
    return {"services": results, "total": len(results), "ready": ready_count,
            "not_ready": len(results) - ready_count,
            "readiness_pct": round(ready_count / max(len(results), 1) * 100, 1)}
