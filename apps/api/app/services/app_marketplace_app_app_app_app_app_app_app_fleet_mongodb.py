"""Fleet MongoDB — track MongoDB replica set health."""
from __future__ import annotations
def fleet_mongodb_status(members: list[dict]) -> dict:
    primary = [m for m in members if m.get("state") == "PRIMARY"]
    secondary = [m for m in members if m.get("state") == "SECONDARY"]
    max_lag_sec = max((m.get("replication_lag_sec", 0) for m in secondary), default=0)
    return {"members": len(members), "primary": len(primary), "secondary": len(secondary),
            "max_lag_sec": max_lag_sec, "healthy": len(primary) == 1 and max_lag_sec < 10}
