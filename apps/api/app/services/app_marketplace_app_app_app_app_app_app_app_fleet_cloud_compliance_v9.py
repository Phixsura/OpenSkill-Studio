"""Fleet Cloud Compliance v9 — track CIS benchmark compliance."""
from __future__ import annotations
def fleet_cloud_compliance_v9(benchmarks: list[dict]) -> dict:
    passed = sum(b.get("passed", 0) for b in benchmarks)
    failed = sum(b.get("failed", 0) for b in benchmarks)
    score = round(passed / (passed + failed) * 100, 1) if (passed + failed) else 0
    return {"benchmarks": len(benchmarks), "passed": passed, "failed": failed,
            "compliance_score": score, "healthy": failed == 0}
