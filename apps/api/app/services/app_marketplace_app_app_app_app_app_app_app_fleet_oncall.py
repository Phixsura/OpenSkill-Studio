"""Fleet on-call rotation — track on-call schedule and load."""
from __future__ import annotations
def fleet_oncall_status(rotations: list[dict]) -> dict:
    active = [r for r in rotations if r.get("on_call")]
    overloaded = [r for r in rotations if r.get("pages_24h", 0) > 10]
    return {"rotations": len(rotations), "active_oncall": len(active),
            "overloaded": len(overloaded), "healthy": len(overloaded) == 0}
