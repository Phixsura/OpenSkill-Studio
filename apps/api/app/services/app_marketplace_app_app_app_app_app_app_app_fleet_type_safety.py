"""Fleet type safety — track typed vs untyped code."""
from __future__ import annotations
def fleet_type_safety(repos: list[dict]) -> dict:
    typed = [r for r in repos if r.get("strict_types", False)]
    coverage = round(sum(r.get("type_coverage_pct", 0) for r in repos) / max(len(repos), 1), 1)
    return {"total": len(repos), "strict_typed": len(typed),
            "avg_coverage_pct": coverage, "type_safe": coverage >= 80}
