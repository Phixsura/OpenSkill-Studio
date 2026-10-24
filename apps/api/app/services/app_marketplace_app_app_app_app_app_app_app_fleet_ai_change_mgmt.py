"""Fleet AI Change Management — track AI model change approval workflows."""
from __future__ import annotations
def fleet_ai_change_mgmt(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    changes_24h = sum(s.get("changes_24h", 0) for s in systems)
    approved = sum(s.get("approved", 0) for s in systems)
    rejected = sum(s.get("rejected", 0) for s in systems)
    return {"systems": len(systems), "active": len(active), "changes_24h": changes_24h,
            "approved": approved, "rejected": rejected, "governed": changes_24h > 0}
