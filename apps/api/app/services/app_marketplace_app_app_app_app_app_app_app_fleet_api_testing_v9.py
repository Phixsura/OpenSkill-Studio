"""Fleet API Testing v9 — track automated API test suite results."""
from __future__ import annotations
def fleet_api_testing_v9(suites: list[dict]) -> dict:
    passed = sum(s.get("passed", 0) for s in suites)
    failed = sum(s.get("failed", 0) for s in suites)
    skipped = sum(s.get("skipped", 0) for s in suites)
    coverage = sum(s.get("endpoint_coverage_pct", 0) for s in suites) / len(suites) if suites else 0
    return {"suites": len(suites), "passed": passed, "failed": failed, "skipped": skipped,
            "avg_coverage_pct": round(coverage, 1), "healthy": failed == 0}
