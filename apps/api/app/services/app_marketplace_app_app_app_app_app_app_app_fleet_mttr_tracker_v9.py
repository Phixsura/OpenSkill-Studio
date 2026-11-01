"""Fleet MTTR Tracker v9 — track DORA mean time to recovery metric."""
from __future__ import annotations
def fleet_mttr_tracker_v9(incidents: list[dict]) -> dict:
    times = [i.get("recovery_min", 0) for i in incidents]
    avg = sum(times) / len(times) if times else 0
    max_time = max(times) if times else 0
    return {"incidents": len(incidents), "avg_mttr_min": round(avg, 1), "max_mttr_min": max_time,
            "dora_class": "Elite" if avg < 60 else "High" if avg < 1440 else "Medium",
            "healthy": avg < 60}
