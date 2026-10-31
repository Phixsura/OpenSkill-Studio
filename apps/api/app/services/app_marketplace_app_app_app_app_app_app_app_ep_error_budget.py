"""Endpoint error budget — track error budget per endpoint."""
from __future__ import annotations


def endpoint_error_budget(endpoint: str, total_requests: int, failed: int,
                          slo_target: float = 99.9) -> dict:
    budget = round((1 - slo_target / 100) * total_requests)
    consumed = failed
    remaining = max(0, budget - consumed)
    pct_consumed = round(consumed / max(budget, 1) * 100, 1)
    exhausted = consumed >= budget
    return {"endpoint": endpoint, "budget": budget, "consumed": consumed,
            "remaining": remaining, "pct_consumed": pct_consumed,
            "exhausted": exhausted, "slo_target": slo_target}


def fleet_error_budgets(endpoints: list[dict]) -> dict:
    results = [endpoint_error_budget(e["endpoint"], e["total"], e["failed"],
                                      e.get("slo_target", 99.9)) for e in endpoints]
    exhausted = sum(1 for r in results if r["exhausted"])
    return {"endpoints": results, "total": len(results), "exhausted": exhausted,
            "all_within_budget": exhausted == 0}
