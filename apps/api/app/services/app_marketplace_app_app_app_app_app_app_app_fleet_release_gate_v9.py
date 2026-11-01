"""Fleet Release Gate v9 — track release quality gates and approvals."""
from __future__ import annotations
def fleet_release_gate_v9(releases: list[dict]) -> dict:
    passed = [r for r in releases if r.get("all_gates_passed")]
    blocked = [r for r in releases if r.get("blocked")]
    gates_total = sum(r.get("gates", 0) for r in releases)
    return {"releases": len(releases), "passed": len(passed), "blocked": len(blocked),
            "total_gates": gates_total, "healthy": len(blocked) == 0}
