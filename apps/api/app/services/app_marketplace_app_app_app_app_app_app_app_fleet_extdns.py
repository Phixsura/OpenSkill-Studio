"""Fleet external-dns — track DNS record management."""
from __future__ import annotations
def fleet_extdns_status(records: list[dict]) -> dict:
    synced = [r for r in records if r.get("synced", True)]
    stale = [r for r in records if r.get("stale", False)]
    return {"total": len(records), "synced": len(synced), "stale": len(stale),
            "healthy": len(stale) == 0}
