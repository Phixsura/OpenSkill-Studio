"""Fleet AI Token Billing v3 — track per-token cost metering and billing."""
from __future__ import annotations
def fleet_ai_token_billing_v3(meters: list[dict]) -> dict:
    active = [m for m in meters if m.get("active", True)]
    tokens_24h = sum(m.get("tokens_24h", 0) for m in meters)
    revenue = round(sum(m.get("revenue_usd", 0) for m in meters), 2)
    customers = sum(m.get("customers", 0) for m in meters)
    return {"meters": len(meters), "active": len(active), "tokens_24h": tokens_24h,
            "revenue_usd": revenue, "customers": customers, "billing": revenue > 0}
