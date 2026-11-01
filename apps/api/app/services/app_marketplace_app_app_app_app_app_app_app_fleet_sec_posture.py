"""Fleet security posture — overall security assessment."""
from __future__ import annotations
def fleet_security_posture(checks: list[dict]) -> dict:
    passed = [c for c in checks if c.get("passed", False)]
    critical_fails = [c for c in checks if not c.get("passed", False) and c.get("severity") == "critical"]
    score = round(len(passed) / max(len(checks), 1) * 100, 1)
    grade = "A" if score >= 95 and len(critical_fails) == 0 else ("B" if score >= 80 else ("C" if score >= 60 else "F"))
    return {"total": len(checks), "passed": len(passed), "critical_fails": len(critical_fails),
            "score": score, "grade": grade}
