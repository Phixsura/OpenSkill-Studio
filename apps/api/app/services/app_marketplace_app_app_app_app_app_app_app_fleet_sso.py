"""Fleet SSO status — track SSO/IdP integration health."""
from __future__ import annotations
def fleet_sso_status(providers: list[dict]) -> dict:
    healthy = [p for p in providers if p.get("status") == "healthy"]
    degraded = [p for p in providers if p.get("status") == "degraded"]
    return {"total": len(providers), "healthy": len(healthy),
            "degraded": len(degraded), "down": len(providers) - len(healthy) - len(degraded),
            "all_ok": len(healthy) == len(providers)}
