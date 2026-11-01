"""Fleet A/B Test v9 — track experiment results and statistical significance."""
from __future__ import annotations
def fleet_ab_test_v9(experiments: list[dict]) -> dict:
    running = [e for e in experiments if e.get("status") == "running"]
    significant = [e for e in experiments if e.get("significant")]
    avg_lift = sum(e.get("lift_pct", 0) for e in experiments if e.get("significant")) / len(significant) if significant else 0
    return {"total": len(experiments), "running": len(running), "significant": len(significant),
            "avg_lift_pct": round(avg_lift, 1), "healthy": True}
