"""Fleet TLS cert expiry — track certificate expiration across services."""
from __future__ import annotations
def fleet_tls_expiry(certs: list[dict]) -> dict:
    expiring = [c for c in certs if c.get("days_left", 999) < 30]
    expired = [c for c in certs if c.get("days_left", 999) <= 0]
    return {"total": len(certs), "expiring_soon": len(expiring),
            "expired": len(expired), "all_valid": len(expired) == 0 and len(expiring) == 0}
