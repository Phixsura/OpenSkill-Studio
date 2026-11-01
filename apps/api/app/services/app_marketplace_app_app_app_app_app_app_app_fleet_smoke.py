"""Fleet smoke tests — track post-deploy smoke test results."""
from __future__ import annotations
def fleet_smoke_tests(deployments: list[dict]) -> dict:
    passed = [d for d in deployments if d.get("smoke_passed", True)]
    failed = len(deployments) - len(passed)
    return {"total": len(deployments), "passed": len(passed), "failed": failed,
            "all_passed": failed == 0}
