"""Fleet Synthetic Monitor v9 — track synthetic transaction monitoring."""
from __future__ import annotations
def fleet_synthetic_monitor_v9(checks: list[dict]) -> dict:
    passing = [c for c in checks if c.get("passing")]
    failing = [c for c in checks if not c.get("passing")]
    avg_duration = sum(c.get("duration_ms", 0) for c in checks) / len(checks) if checks else 0
    return {"checks": len(checks), "passing": len(passing), "failing": len(failing),
            "avg_duration_ms": round(avg_duration, 1), "healthy": len(failing) == 0}
