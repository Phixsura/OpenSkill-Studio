"""Deployment health check — verify deployment health post-deploy."""
from __future__ import annotations


def post_deploy_check(checks: list[dict]) -> dict:
    results = []
    for c in checks:
        passed = c.get("passed", False)
        results.append({"name": c["name"], "passed": passed,
                        "duration_ms": c.get("duration_ms", 0),
                        "message": c.get("message", "")})
    all_passed = all(r["passed"] for r in results)
    failed = [r["name"] for r in results if not r["passed"]]
    total_ms = sum(r["duration_ms"] for r in results)
    return {"healthy": all_passed, "checks": results,
            "passed": sum(1 for r in results if r["passed"]),
            "failed": len(failed), "failed_checks": failed,
            "total_ms": round(total_ms, 1)}


def should_rollback(health: dict, auto_rollback_threshold: int = 1) -> dict:
    rollback = health.get("failed", 0) >= auto_rollback_threshold
    return {"rollback": rollback, "failed_count": health.get("failed", 0),
            "threshold": auto_rollback_threshold,
            "recommendation": "rollback" if rollback else "proceed"}
