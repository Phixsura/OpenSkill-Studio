"""Fleet AI Identity v8 — track ultimate zero-trust identity management."""
from __future__ import annotations
def fleet_ai_identity_v8(providers: list[dict]) -> dict:
    active = [p for p in providers if p.get("active", True)]
    users = sum(p.get("users", 0) for p in providers)
    auth = sum(p.get("auth_24h", 0) for p in providers)
    mfa = round(sum(p.get("mfa_pct", 0) for p in providers) / max(len(providers), 1), 1)
    zt = all(p.get("zt", False) for p in providers)
    return {"providers": len(providers), "active": len(active), "users": users,
            "auth": auth, "mfa": mfa, "zt": zt, "secure": zt and mfa > 95}
