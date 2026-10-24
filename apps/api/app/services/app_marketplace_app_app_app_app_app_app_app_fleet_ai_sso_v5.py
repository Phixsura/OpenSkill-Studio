"""Fleet AI SSO v5 — track enterprise single sign-on at global scale."""
from __future__ import annotations
def fleet_ai_sso_v5(providers: list[dict]) -> dict:
    active = [p for p in providers if p.get("active", True)]
    logins_24h = sum(p.get("logins", 0) for p in providers)
    protocols = set()
    for p in providers:
        protocols.update(p.get("protocols", []))
    mfa_enforced = all(p.get("mfa", False) for p in providers)
    return {"providers": len(providers), "active": len(active), "logins_24h": logins_24h,
            "protocols": sorted(protocols), "mfa_enforced": mfa_enforced, "enterprise": len(protocols) > 2}
