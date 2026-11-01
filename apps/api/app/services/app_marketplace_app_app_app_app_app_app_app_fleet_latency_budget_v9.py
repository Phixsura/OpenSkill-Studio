"""Fleet Latency Budget v9 — track p50/p95/p99 latency budgets."""
from __future__ import annotations
def fleet_latency_budget_v9(services: list[dict]) -> dict:
    within_budget = [s for s in services if s.get("p99_ms", 0) < s.get("budget_ms", 500)]
    avg_p99 = sum(s.get("p99_ms", 0) for s in services) / len(services) if services else 0
    return {"services": len(services), "within_budget": len(within_budget),
            "avg_p99_ms": round(avg_p99, 1), "healthy": len(within_budget) == len(services)}
