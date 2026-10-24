"""Fleet cert-manager — track certificate lifecycle."""
from __future__ import annotations
def fleet_certmgr_status(certs: list[dict]) -> dict:
    ready = [c for c in certs if c.get("ready", False)]
    expiring = [c for c in certs if c.get("days_to_expiry", 999) < 30]
    failed_renewal = [c for c in certs if c.get("renewal_failed", False)]
    return {"total": len(certs), "ready": len(ready), "expiring": len(expiring),
            "failed_renewal": len(failed_renewal), "healthy": len(expiring) == 0 and len(failed_renewal) == 0}
