"""Fleet AI SSO — track single sign-on for AI platform access."""
from __future__ import annotations
def fleet_ai_sso(providers: list[dict]) -> dict:
    active = [p for p in providers if p.get("active", True)]
    logins_24h = sum(p.get("logins_24h", 0) for p in providers)
    protocols = set()
    for p in providers:
        protocols.update(p.get("protocols", []))
    mfa_pct = round(sum(p.get("mfa_pct", 0) for p in providers) / max(len(providers), 1), 1)
    return {"providers": len(providers), "active": len(active), "logins_24h": logins_24h,
            "protocols": sorted(protocols), "mfa_pct": mfa_pct, "secure": mfa_pct > 90}
