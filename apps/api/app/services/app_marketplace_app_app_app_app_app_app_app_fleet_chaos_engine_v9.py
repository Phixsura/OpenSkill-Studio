"""Fleet Chaos Engine v9 — track chaos experiments and blast radius."""
from __future__ import annotations
def fleet_chaos_engine_v9(experiments: list[dict]) -> dict:
    completed = [e for e in experiments if e.get("status") == "completed"]
    failed = [e for e in experiments if e.get("status") == "failed"]
    avg_blast = sum(e.get("blast_radius", 0) for e in experiments) / len(experiments) if experiments else 0
    return {"total": len(experiments), "completed": len(completed), "failed": len(failed),
            "avg_blast_radius": round(avg_blast, 1), "healthy": len(failed) == 0}
