"""Fleet Chaos Monkey v9 — random instance termination for resilience testing."""
from __future__ import annotations
def fleet_chaos_monkey_v9(targets: list[dict]) -> dict:
    terminated = sum(t.get("terminated_today", 0) for t in targets)
    recovered = sum(t.get("auto_recovered", 0) for t in targets)
    avg_recovery = sum(t.get("recovery_sec", 0) for t in targets) / len(targets) if targets else 0
    return {"targets": len(targets), "terminated_today": terminated, "auto_recovered": recovered,
            "avg_recovery_sec": round(avg_recovery, 1), "healthy": recovered >= terminated}
