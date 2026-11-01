"""Fleet Resend — track modern email API health."""
from __future__ import annotations
def fleet_resend_status(domains: list[dict]) -> dict:
    verified = [d for d in domains if d.get("verified", True)]
    emails_24h = sum(d.get("emails_24h", 0) for d in domains)
    delivery_rate = round(sum(d.get("delivery_rate", 100) for d in domains) / max(len(domains), 1), 1)
    return {"domains": len(domains), "verified": len(verified), "emails_24h": emails_24h,
            "delivery_rate": delivery_rate, "all_verified": len(verified) == len(domains)}
