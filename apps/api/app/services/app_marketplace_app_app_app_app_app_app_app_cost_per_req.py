"""Service cost per request — calculate cost per API request."""
from __future__ import annotations


def calculate_cost_per_request(infra_cost: float, total_requests: int) -> dict:
    cpp = round(infra_cost / max(total_requests, 1) * 1000, 4)  # cost per 1000 requests
    return {"infra_cost": infra_cost, "total_requests": total_requests,
            "cost_per_1k_requests": cpp,
            "cost_per_million": round(cpp * 1000, 2)}


def cost_by_endpoint(endpoints: list[dict], total_cost: float) -> list[dict]:
    total_reqs = sum(e.get("requests", 0) for e in endpoints)
    results = []
    for ep in endpoints:
        share = ep["requests"] / max(total_reqs, 1)
        cost = round(total_cost * share, 2)
        per_1k = round(cost / max(ep["requests"], 1) * 1000, 4)
        results.append({"endpoint": ep["endpoint"], "requests": ep["requests"],
                        "cost": cost, "cost_per_1k": per_1k, "share_pct": round(share * 100, 1)})
    return sorted(results, key=lambda r: -r["cost"])
