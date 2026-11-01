"""Fleet architecture fitness — track architectural fitness functions."""
from __future__ import annotations
def fleet_arch_fitness(functions: list[dict]) -> dict:
    passing = [f for f in functions if f.get("passed", False)]
    score = round(len(passing) / max(len(functions), 1) * 100, 1)
    return {"total": len(functions), "passing": len(passing),
            "failing": len(functions) - len(passing), "score": score, "fit": score >= 90}
