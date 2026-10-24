"""Fleet code duplication — track code clone metrics."""
from __future__ import annotations
def fleet_code_duplication(analysis: dict) -> dict:
    dup_pct = analysis.get("duplication_pct", 0)
    clones = analysis.get("clone_count", 0)
    return {"duplication_pct": dup_pct, "clones": clones,
            "acceptable": dup_pct <= 5, "needs_refactor": dup_pct > 10}
