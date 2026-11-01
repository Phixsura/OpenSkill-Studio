"""Fleet Chaos Report v9 — aggregate chaos engineering results."""
from __future__ import annotations
def fleet_chaos_report_v9(reports: list[dict]) -> dict:
    passed = [r for r in reports if r.get("result") == "passed"]
    failed = [r for r in reports if r.get("result") == "failed"]
    improvements = sum(r.get("improvements_found", 0) for r in reports)
    return {"reports": len(reports), "passed": len(passed), "failed": len(failed),
            "improvements_found": improvements, "healthy": len(failed) == 0}
