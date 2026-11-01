"""Fleet Auth0 — track identity platform health."""
from __future__ import annotations
def fleet_auth0_status(tenants: list[dict]) -> dict:
    active = [t for t in tenants if t.get("active", True)]
    total_logins = sum(t.get("logins_24h", 0) for t in tenants)
    mfa_pct = round(sum(t.get("mfa_pct", 0) for t in tenants) / max(len(tenants), 1), 1)
    return {"tenants": len(tenants), "active": len(active), "logins_24h": total_logins,
            "mfa_pct": mfa_pct, "secure": mfa_pct >= 80}
