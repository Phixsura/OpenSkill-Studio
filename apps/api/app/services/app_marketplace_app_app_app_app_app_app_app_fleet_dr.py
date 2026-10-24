"""Fleet DR readiness — disaster recovery readiness check."""
from __future__ import annotations
def fleet_dr_readiness(checks: list[dict]) -> dict:
    passed = [c for c in checks if c.get("passed", False)]
    last_drill = max((c.get("last_drill_days", 999) for c in checks), default=999)
    return {"total": len(checks), "passed": len(passed),
            "failed": len(checks) - len(passed), "last_drill_days": last_drill,
            "ready": len(passed) == len(checks) and last_drill <= 90}
