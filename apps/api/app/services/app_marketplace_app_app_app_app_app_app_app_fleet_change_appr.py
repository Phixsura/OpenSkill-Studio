"""Fleet change approval — track change management compliance."""
from __future__ import annotations
def fleet_change_approval(changes: list[dict]) -> dict:
    approved = [c for c in changes if c.get("approved", False)]
    emergency = [c for c in changes if c.get("type") == "emergency"]
    return {"total": len(changes), "approved": len(approved),
            "unapproved": len(changes) - len(approved), "emergency": len(emergency),
            "compliant": len(approved) == len(changes)}
