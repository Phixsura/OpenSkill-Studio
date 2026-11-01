"""Deployment dependency checker — verify deploy prerequisites."""
from __future__ import annotations


def check_deploy_deps(service: str, prerequisites: list[dict]) -> dict:
    results = []
    blocking = 0
    for p in prerequisites:
        passed = p.get("status") == "ready"
        if not passed and p.get("required", True):
            blocking += 1
        results.append({"name": p["name"], "type": p.get("type", "service"),
                         "status": p.get("status", "unknown"), "passed": passed,
                         "required": p.get("required", True)})
    can_deploy = blocking == 0
    return {"service": service, "prerequisites": results, "total": len(results),
            "passed": sum(1 for r in results if r["passed"]),
            "blocking": blocking, "can_deploy": can_deploy}
