"""Service dependency timeout calculator — compute safe timeout values."""
from __future__ import annotations


def calculate_timeout(dep_chain: list[dict]) -> dict:
    total_p99 = 0
    total_budget = 0
    for dep in dep_chain:
        p99 = dep.get("p99_ms", 0)
        budget = dep.get("timeout_ms", 0)
        total_p99 += p99
        total_budget += budget
    safety_margin = round(total_p99 * 0.2)  # 20% margin
    recommended = total_p99 + safety_margin
    over_budget = recommended > total_budget if total_budget > 0 else False
    return {"chain_p99_ms": total_p99, "safety_margin_ms": safety_margin,
            "recommended_timeout_ms": recommended, "current_budget_ms": total_budget,
            "over_budget": over_budget, "deps_in_chain": len(dep_chain)}


def timeout_summary(chains: list[dict]) -> dict:
    over_budget = sum(1 for c in chains if c.get("over_budget"))
    return {"total_chains": len(chains), "over_budget": over_budget,
            "all_ok": over_budget == 0}
