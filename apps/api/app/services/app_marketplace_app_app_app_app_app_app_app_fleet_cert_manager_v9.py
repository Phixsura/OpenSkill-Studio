"""Fleet Cert Manager v9 — track TLS certificate lifecycle."""
from __future__ import annotations
def fleet_cert_manager_v9(certs: list[dict]) -> dict:
    valid = [c for c in certs if c.get("valid", True)]
    expiring = [c for c in certs if c.get("days_to_expiry", 999) < 30]
    return {"total": len(certs), "valid": len(valid), "expiring_soon": len(expiring),
            "auto_renewed": sum(1 for c in certs if c.get("auto_renew")),
            "healthy": len(expiring) == 0}
