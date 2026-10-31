"""Fleet AI Model Billing v2 — track per-model consumption billing."""
from __future__ import annotations
def fleet_ai_model_billing_v2(billers: list[dict]) -> dict:
    active = [b for b in billers if b.get("active", True)]
    models = sum(b.get("models", 0) for b in billers)
    revenue_24h = round(sum(b.get("revenue_usd", 0) for b in billers), 2)
    invoices = sum(b.get("invoices", 0) for b in billers)
    return {"billers": len(billers), "active": len(active), "models": models,
            "revenue_usd": revenue_24h, "invoices": invoices, "monetized": revenue_24h > 0}
