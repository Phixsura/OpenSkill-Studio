"""Deployment guard rails — enforce safety checks before deploy."""
from __future__ import annotations


GUARDS = {
    "tests_pass": {"description": "All tests passing", "blocking": True},
    "no_critical_vulns": {"description": "No critical vulnerabilities", "blocking": True},
    "approval": {"description": "Required approvals received", "blocking": True},
    "performance_budget": {"description": "Within performance budget", "blocking": False},
    "no_deploy_freeze": {"description": "No active deploy freeze", "blocking": True},
    "canary_healthy": {"description": "Canary deployment healthy", "blocking": False},
}


def check_guards(statuses: dict[str, bool]) -> dict:
    results = []
    blocking_failures = 0
    for guard_id, info in GUARDS.items():
        passed = statuses.get(guard_id, False)
        if not passed and info["blocking"]:
            blocking_failures += 1
        results.append({"guard": guard_id, **info, "passed": passed})
    can_deploy = blocking_failures == 0
    total_passed = sum(1 for r in results if r["passed"])
    return {"guards": results, "total": len(results), "passed": total_passed,
            "blocking_failures": blocking_failures, "can_deploy": can_deploy}
