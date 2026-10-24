"""Latency budget tracker — allocate and track latency budgets per endpoint."""
from __future__ import annotations


def allocate_latency_budget(endpoint: str, total_budget_ms: int,
                              stages: list[dict]) -> dict:
    allocated = 0
    results = []
    for s in stages:
        alloc = s.get("budget_ms", 0)
        allocated += alloc
        results.append({"stage": s["name"], "budget_ms": alloc,
                         "actual_ms": s.get("actual_ms", 0),
                         "within_budget": s.get("actual_ms", 0) <= alloc})
    remaining = total_budget_ms - allocated
    over_budget = any(not r["within_budget"] for r in results)
    return {"endpoint": endpoint, "total_budget_ms": total_budget_ms,
            "allocated_ms": allocated, "remaining_ms": remaining,
            "stages": results, "over_budget": over_budget}
