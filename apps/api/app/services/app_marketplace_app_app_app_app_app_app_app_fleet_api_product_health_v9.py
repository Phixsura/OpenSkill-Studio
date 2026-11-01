"""Fleet API Product Health v9 — track API product-level health metrics."""
from __future__ import annotations
def fleet_api_product_health_v9(products: list[dict]) -> dict:
    healthy_p = [p for p in products if p.get("healthy")]
    revenue = sum(p.get("monthly_revenue", 0) for p in products)
    adoption = sum(p.get("adoption_pct", 0) for p in products) / len(products) if products else 0
    return {"products": len(products), "healthy": len(healthy_p), "monthly_revenue": round(revenue, 2),
            "avg_adoption_pct": round(adoption, 1), "all_healthy": len(healthy_p) == len(products)}
