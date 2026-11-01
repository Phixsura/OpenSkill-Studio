"""Fleet GCP Cloud Functions — track serverless health."""
from __future__ import annotations
def fleet_gcf_status(functions: list[dict]) -> dict:
    active = [f for f in functions if f.get("status") == "ACTIVE"]
    total_exec = sum(f.get("executions_24h", 0) for f in functions)
    avg_dur = round(sum(f.get("avg_duration_ms", 0) for f in functions) / max(len(functions), 1), 1)
    return {"functions": len(functions), "active": len(active), "executions_24h": total_exec,
            "avg_duration_ms": avg_dur, "all_active": len(active) == len(functions)}
