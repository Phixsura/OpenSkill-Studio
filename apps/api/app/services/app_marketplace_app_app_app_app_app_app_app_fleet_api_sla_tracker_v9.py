"""Fleet API SLA Tracker v9 — track SLA commitments per API tier."""
from __future__ import annotations
def fleet_api_sla_tracker_v9(slas: list[dict]) -> dict:
    met = [s for s in slas if s.get("met")]
    breached = [s for s in slas if s.get("breached")]
    credits_owed = sum(s.get("credits_owed", 0) for s in slas)
    return {"slas": len(slas), "met": len(met), "breached": len(breached),
            "credits_owed": round(credits_owed, 2), "healthy": len(breached) == 0}
