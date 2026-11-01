"""Fleet Chaos Testing v9 — track chaos testing maturity and coverage."""
from __future__ import annotations
def fleet_chaos_testing_v9(services: list[dict]) -> dict:
    tested = [s for s in services if s.get("chaos_tested")]
    resilient = [s for s in services if s.get("passed_chaos")]
    coverage = round(len(tested) / len(services) * 100, 1) if services else 0
    return {"services": len(services), "chaos_tested": len(tested), "resilient": len(resilient),
            "coverage_pct": coverage, "healthy": coverage > 80}
