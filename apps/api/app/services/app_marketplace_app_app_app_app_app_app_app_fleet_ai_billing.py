"""Fleet AI Billing Meter — track AI consumption-based billing."""
from __future__ import annotations
def fleet_ai_billing(meters: list[dict]) -> dict:
    active = [m for m in meters if m.get("active", True)]
    revenue_24h = round(sum(m.get("revenue_usd", 0) for m in meters), 2)
    invoices_generated = sum(m.get("invoices", 0) for m in meters)
    customers = sum(m.get("customers", 0) for m in meters)
    return {"meters": len(meters), "active": len(active), "revenue_usd": revenue_24h,
            "invoices": invoices_generated, "customers": customers, "monetized": revenue_24h > 0}
