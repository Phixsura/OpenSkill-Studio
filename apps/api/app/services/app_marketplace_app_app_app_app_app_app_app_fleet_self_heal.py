"""Fleet self-healing — track automated recovery actions."""
from __future__ import annotations
def fleet_self_healing(events: list[dict]) -> dict:
    auto_recovered = [e for e in events if e.get("auto_recovered", False)]
    manual = [e for e in events if not e.get("auto_recovered", False)]
    rate = round(len(auto_recovered) / max(len(events), 1) * 100, 1)
    return {"total": len(events), "auto_recovered": len(auto_recovered),
            "manual": len(manual), "automation_rate": rate, "mature": rate >= 80}
