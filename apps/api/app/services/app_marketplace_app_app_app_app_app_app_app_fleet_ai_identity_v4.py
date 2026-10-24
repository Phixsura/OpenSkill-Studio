"""Fleet AI Identity v4 — track zero-trust identity management."""
from __future__ import annotations
def fleet_ai_identity_v4(providers: list[dict]) -> dict:
    active = [p for p in providers if p.get("active", True)]
    users = sum(p.get("users", 0) for p in providers)
    auth_24h = sum(p.get("auth_24h", 0) for p in providers)
    mfa_pct = round(sum(p.get("mfa_pct", 0) for p in providers) / max(len(providers), 1), 1)
    zero_trust = all(p.get("zero_trust", False) for p in providers)
    return {"providers": len(providers), "active": len(active), "users": users,
            "auth_24h": auth_24h, "mfa_pct": mfa_pct, "zero_trust": zero_trust, "secure": zero_trust and mfa_pct > 90}
