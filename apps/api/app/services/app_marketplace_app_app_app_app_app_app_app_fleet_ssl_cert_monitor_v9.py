"""Fleet SSL Cert Monitor v9 — track SSL certificate expiry monitoring."""
from __future__ import annotations
def fleet_ssl_cert_monitor_v9(certs: list[dict]) -> dict:
    valid = [c for c in certs if c.get("valid")]
    expiring = [c for c in certs if c.get("days_to_expiry", 999) < 30]
    auto_renew = [c for c in certs if c.get("auto_renew")]
    return {"certs": len(certs), "valid": len(valid), "expiring_30d": len(expiring),
            "auto_renew": len(auto_renew), "healthy": len(expiring) == 0}
