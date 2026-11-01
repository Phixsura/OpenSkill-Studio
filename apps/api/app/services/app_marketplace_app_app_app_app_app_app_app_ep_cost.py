"""API endpoint cost analyzer — analyze cost per endpoint."""
from __future__ import annotations


def analyze_endpoint_cost(endpoints: list[dict], total_infra_cost: float) -> dict:
    total_compute = sum(e.get("compute_units", 0) for e in endpoints)
    results = []
    for ep in endpoints:
        share = ep.get("compute_units", 0) / max(total_compute, 0.01)
        cost = round(total_infra_cost * share, 2)
        per_req = round(cost / max(ep.get("requests", 1), 1) * 1000, 4)
        results.append({"endpoint": ep["endpoint"], "cost": cost, "cost_per_1k": per_req,
                        "share_pct": round(share * 100, 1), "requests": ep.get("requests", 0)})
    return {"endpoints": sorted(results, key=lambda r: -r["cost"]),
            "total_cost": total_infra_cost}


def identify_expensive(endpoints: list[dict], threshold_per_1k: float = 1.0) -> list[dict]:
    return [e for e in endpoints if e.get("cost_per_1k", 0) > threshold_per_1k]
