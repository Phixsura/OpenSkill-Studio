"""Fleet scaling history — track scaling event history."""
from __future__ import annotations
def fleet_scaling_history(events: list[dict]) -> dict:
    ups = [e for e in events if e.get("direction") == "up"]
    downs = [e for e in events if e.get("direction") == "down"]
    return {"total": len(events), "scale_ups": len(ups), "scale_downs": len(downs),
            "ratio": round(len(ups) / max(len(downs), 1), 2)}
