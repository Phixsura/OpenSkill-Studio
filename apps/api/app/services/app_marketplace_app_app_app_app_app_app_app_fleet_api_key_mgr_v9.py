"""Fleet API Key Manager v9 — track API key issuance and revocation."""
from __future__ import annotations
def fleet_api_key_mgr_v9(keys: list[dict]) -> dict:
    active = [k for k in keys if k.get("active")]
    revoked = [k for k in keys if k.get("revoked")]
    expired = [k for k in keys if k.get("expired")]
    return {"total": len(keys), "active": len(active), "revoked": len(revoked),
            "expired": len(expired), "healthy": len(expired) == 0}
