"""Fleet SaltStack — track event-driven infrastructure automation."""
from __future__ import annotations
def fleet_salt_status(minions: list[dict]) -> dict:
    connected = [m for m in minions if m.get("connected", True)]
    grains_ok = [m for m in minions if m.get("grains_sync", True)]
    return {"total": len(minions), "connected": len(connected),
            "disconnected": len(minions) - len(connected),
            "grains_synced": len(grains_ok), "healthy": len(connected) == len(minions)}
