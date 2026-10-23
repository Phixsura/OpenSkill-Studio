"""SSL certificate monitor — track cert expiry and renewal status."""
from __future__ import annotations


def check_certificates(certs: list[dict], *, warn_days: int = 30) -> dict:
    results = []
    expiring_soon = 0
    expired = 0
    for c in certs:
        days_left = c.get("days_until_expiry", 0)
        status = "expired" if days_left <= 0 else "expiring" if days_left <= warn_days else "valid"
        if status == "expired":
            expired += 1
        elif status == "expiring":
            expiring_soon += 1
        results.append({
            "domain": c["domain"], "issuer": c.get("issuer", ""),
            "days_until_expiry": days_left, "status": status,
            "auto_renew": c.get("auto_renew", False),
        })
    results.sort(key=lambda r: r["days_until_expiry"])
    healthy = len(certs) - expired - expiring_soon
    return {"total": len(certs), "valid": healthy, "expiring_soon": expiring_soon,
            "expired": expired, "results": results,
            "overall": "critical" if expired > 0 else "warning" if expiring_soon > 0 else "healthy"}
