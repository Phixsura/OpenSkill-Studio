"""Billing summary — monthly billing breakdown for developer apps."""


def build_billing_summary(*, executions: int, webhooks: int, api_calls: int, storage_mb: float,
                           tier: str = "standard") -> dict:
    rates = {"standard": {"exec": 0.001, "webhook": 0.0001, "api": 0.00005, "storage": 0.05},
             "premium": {"exec": 0.0008, "webhook": 0.00008, "api": 0.00004, "storage": 0.04}}
    r = rates.get(tier, rates["standard"])
    items = [
        {"item": "Executions", "qty": executions, "rate": r["exec"], "cost": round(executions * r["exec"], 4)},
        {"item": "Webhooks", "qty": webhooks, "rate": r["webhook"], "cost": round(webhooks * r["webhook"], 4)},
        {"item": "API Calls", "qty": api_calls, "rate": r["api"], "cost": round(api_calls * r["api"], 4)},
        {"item": "Storage", "qty": round(storage_mb, 1), "rate": r["storage"], "cost": round(storage_mb * r["storage"], 4)},
    ]
    total = round(sum(i["cost"] for i in items), 2)
    return {"items": items, "total_usd": total, "tier": tier}
