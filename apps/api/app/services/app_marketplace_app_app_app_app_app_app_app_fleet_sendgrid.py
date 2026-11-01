"""Fleet SendGrid — track email delivery platform."""
from __future__ import annotations
def fleet_sendgrid_status(accounts: list[dict]) -> dict:
    active = [a for a in accounts if a.get("active", True)]
    emails_24h = sum(a.get("emails_24h", 0) for a in accounts)
    delivery_rate = round(sum(a.get("delivery_rate", 100) for a in accounts) / max(len(accounts), 1), 1)
    bounce_rate = round(sum(a.get("bounce_rate", 0) for a in accounts) / max(len(accounts), 1), 2)
    return {"accounts": len(accounts), "active": len(active), "emails_24h": emails_24h,
            "delivery_rate": delivery_rate, "bounce_rate": bounce_rate, "healthy": delivery_rate >= 95}
