"""Fleet Telepresence intercept — track service intercept metrics."""
from __future__ import annotations
def fleet_tp_intercept(intercepts: list[dict]) -> dict:
    active = [i for i in intercepts if i.get("active", False)]
    personal = [i for i in active if i.get("type") == "personal"]
    global_int = [i for i in active if i.get("type") == "global"]
    return {"total": len(intercepts), "active": len(active), "personal": len(personal),
            "global": len(global_int), "in_use": len(active) > 0}
