"""Fleet Disaster Recovery v9 — track DR readiness and failover testing."""
from __future__ import annotations
def fleet_disaster_recovery_v9(plans: list[dict]) -> dict:
    tested = [p for p in plans if p.get("last_test_passed")]
    rpo_met = [p for p in plans if p.get("rpo_met")]
    rto_met = [p for p in plans if p.get("rto_met")]
    return {"plans": len(plans), "tested": len(tested), "rpo_met": len(rpo_met),
            "rto_met": len(rto_met), "healthy": len(tested) == len(plans)}
