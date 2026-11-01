"""SSL certificate monitor — track certificate expiry and renewal."""
from __future__ import annotations


def check_certificates(certs: list[dict]) -> dict:
    expiring_soon = []
    expired = []
    valid = []
    for cert in certs:
        days = cert.get("days_until_expiry", 0)
        entry = {"domain": cert["domain"], "issuer": cert.get("issuer", "unknown"),
                 "days_until_expiry": days}
        if days <= 0:
            expired.append(entry)
        elif days <= 30:
            expiring_soon.append(entry)
        else:
            valid.append(entry)
    return {"valid": len(valid), "expiring_soon": len(expiring_soon),
            "expired": len(expired), "total": len(certs),
            "critical": len(expired) > 0,
            "details": {"valid": valid, "expiring": expiring_soon, "expired": expired}}


def renewal_plan(expiring: list[dict]) -> list[dict]:
    sorted_certs = sorted(expiring, key=lambda c: c["days_until_expiry"])
    plan = []
    for i, cert in enumerate(sorted_certs):
        plan.append({"priority": i + 1, "domain": cert["domain"],
                      "days_left": cert["days_until_expiry"],
                      "action": "renew_immediately" if cert["days_until_expiry"] <= 7 else "schedule_renewal"})
    return plan
