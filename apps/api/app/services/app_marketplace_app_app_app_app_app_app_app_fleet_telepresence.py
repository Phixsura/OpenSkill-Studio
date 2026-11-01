"""Fleet Telepresence — track remote dev connections."""
from __future__ import annotations
def fleet_telepresence_status(sessions: list[dict]) -> dict:
    active = [s for s in sessions if s.get("connected", False)]
    intercepts = sum(s.get("intercepts", 0) for s in active)
    return {"total_sessions": len(sessions), "active": len(active), "intercepts": intercepts,
            "in_use": len(active) > 0}
