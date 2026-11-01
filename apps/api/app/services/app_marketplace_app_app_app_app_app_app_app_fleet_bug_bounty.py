"""Fleet bug bounty — track bug bounty program metrics."""
from __future__ import annotations
def fleet_bug_bounty(reports: list[dict]) -> dict:
    valid = [r for r in reports if r.get("valid", False)]
    paid = sum(r.get("bounty_usd", 0) for r in valid)
    critical = [r for r in valid if r.get("severity") == "critical"]
    return {"total_reports": len(reports), "valid": len(valid), "total_paid": round(paid, 2),
            "critical": len(critical), "active": len(reports) > 0}
