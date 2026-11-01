"""Fleet LitmusChaos — track chaos workflow results."""
from __future__ import annotations
def fleet_litmus_status(workflows: list[dict]) -> dict:
    passed = [w for w in workflows if w.get("result") == "Pass"]
    failed = [w for w in workflows if w.get("result") == "Fail"]
    resilience = round(len(passed) / max(len(workflows), 1) * 100, 1)
    return {"total": len(workflows), "passed": len(passed), "failed": len(failed),
            "resilience_score": resilience, "resilient": resilience >= 80}
