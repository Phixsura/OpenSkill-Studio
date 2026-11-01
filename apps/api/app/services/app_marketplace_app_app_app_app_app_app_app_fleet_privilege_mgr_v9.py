"""Fleet Privilege Manager v9 — track just-in-time privilege elevation."""
from __future__ import annotations
def fleet_privilege_mgr_v9(requests: list[dict]) -> dict:
    approved = [r for r in requests if r.get("status") == "approved"]
    denied = [r for r in requests if r.get("status") == "denied"]
    expired = [r for r in requests if r.get("expired")]
    avg_duration = sum(r.get("duration_min", 0) for r in approved) / len(approved) if approved else 0
    return {"total": len(requests), "approved": len(approved), "denied": len(denied),
            "expired": len(expired), "avg_duration_min": round(avg_duration, 1), "healthy": True}
