"""Fleet scheduling latency — track pod scheduling times."""
from __future__ import annotations
def fleet_scheduling_latency(pods: list[dict]) -> dict:
    times = [p.get("schedule_ms", 0) for p in pods]
    avg = round(sum(times) / max(len(times), 1), 1)
    slow = [t for t in times if t > 5000]
    return {"total": len(pods), "avg_ms": avg, "slow_scheduling": len(slow), "fast": len(slow) == 0}
