"""Fleet Canary Analysis v9 — track automated canary analysis results."""
from __future__ import annotations
def fleet_canary_analysis_v9(analyses: list[dict]) -> dict:
    passed = [a for a in analyses if a.get("result") == "pass"]
    failed = [a for a in analyses if a.get("result") == "fail"]
    metrics_compared = sum(a.get("metrics_compared", 0) for a in analyses)
    return {"analyses": len(analyses), "passed": len(passed), "failed": len(failed),
            "metrics_compared": metrics_compared, "healthy": len(failed) == 0}
