"""Fleet runbook automation — track automated runbook execution."""
from __future__ import annotations
def fleet_runbook_stats(runs: list[dict]) -> dict:
    success = [r for r in runs if r.get("result") == "success"]
    failed = [r for r in runs if r.get("result") == "failed"]
    return {"total": len(runs), "success": len(success), "failed": len(failed),
            "success_rate": round(len(success) / max(len(runs), 1) * 100, 1)}
