"""Fleet game day — track chaos engineering game day results."""
from __future__ import annotations
def fleet_game_day(scenarios: list[dict]) -> dict:
    passed = [s for s in scenarios if s.get("outcome") == "passed"]
    failed = [s for s in scenarios if s.get("outcome") == "failed"]
    learnings = sum(s.get("learnings", 0) for s in scenarios)
    return {"total": len(scenarios), "passed": len(passed), "failed": len(failed),
            "learnings": learnings, "resilient": len(failed) == 0}
