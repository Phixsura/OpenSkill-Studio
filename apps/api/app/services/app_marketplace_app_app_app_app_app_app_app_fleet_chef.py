"""Fleet Chef — track Chef InSpec compliance results."""
from __future__ import annotations
def fleet_chef_compliance(profiles: list[dict]) -> dict:
    passed = sum(p.get("passed", 0) for p in profiles)
    failed = sum(p.get("failed", 0) for p in profiles)
    skipped = sum(p.get("skipped", 0) for p in profiles)
    total = passed + failed + skipped
    pct = round(passed / max(total, 1) * 100, 1)
    return {"profiles": len(profiles), "passed": passed, "failed": failed,
            "skipped": skipped, "compliance_pct": pct, "compliant": failed == 0}
