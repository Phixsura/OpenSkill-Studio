"""Fleet OAuth token stats — track token issuance and revocation."""
from __future__ import annotations
def fleet_oauth_stats(window: dict) -> dict:
    issued = window.get("issued", 0)
    revoked = window.get("revoked", 0)
    expired = window.get("expired", 0)
    active = issued - revoked - expired
    return {"issued": issued, "revoked": revoked, "expired": expired,
            "active": max(active, 0), "revocation_rate": round(revoked / max(issued, 1) * 100, 1)}
