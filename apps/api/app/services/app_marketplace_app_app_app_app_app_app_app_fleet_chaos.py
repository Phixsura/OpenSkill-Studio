"""Fleet chaos experiment — track chaos engineering results."""
from __future__ import annotations
def fleet_chaos_results(experiments: list[dict]) -> dict:
    passed = [e for e in experiments if e.get("passed", False)]
    revealed = [e for e in experiments if e.get("weakness_found", False)]
    return {"total": len(experiments), "passed": len(passed),
            "weaknesses_found": len(revealed), "resilient": len(passed) == len(experiments)}
