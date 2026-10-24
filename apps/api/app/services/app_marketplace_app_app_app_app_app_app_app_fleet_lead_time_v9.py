"""Fleet Lead Time v9 — track DORA lead time for changes metric."""
from __future__ import annotations
def fleet_lead_time_v9(changes: list[dict]) -> dict:
    times = [c.get("lead_time_min", 0) for c in changes]
    avg = sum(times) / len(times) if times else 0
    p95 = sorted(times)[int(len(times) * 0.95)] if times else 0
    return {"changes": len(changes), "avg_lead_time_min": round(avg, 1), "p95_lead_time_min": p95,
            "dora_class": "Elite" if avg < 60 else "High" if avg < 1440 else "Medium",
            "healthy": avg < 60}
