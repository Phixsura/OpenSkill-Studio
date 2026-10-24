"""Fleet readiness assessment — overall platform launch readiness."""
from __future__ import annotations
def fleet_readiness_assessment(checks: list[dict]) -> dict:
    passed = [c for c in checks if c.get("passed", False)]
    blockers = [c for c in checks if not c.get("passed", False) and c.get("blocking", False)]
    score = round(len(passed) / max(len(checks), 1) * 100, 1)
    return {"total_checks": len(checks), "passed": len(passed), "blockers": len(blockers),
            "score": score, "launch_ready": len(blockers) == 0 and score >= 90}
