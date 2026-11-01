"""Fleet Pen Test v9 — track penetration testing results and remediation."""
from __future__ import annotations
def fleet_pen_test_v9(findings: list[dict]) -> dict:
    remediated = [f for f in findings if f.get("remediated")]
    critical = [f for f in findings if f.get("severity") == "critical"]
    open_f = [f for f in findings if not f.get("remediated")]
    return {"total": len(findings), "remediated": len(remediated), "open": len(open_f),
            "critical": len(critical), "healthy": len(critical) == 0 or all(c.get("remediated") for c in critical)}
