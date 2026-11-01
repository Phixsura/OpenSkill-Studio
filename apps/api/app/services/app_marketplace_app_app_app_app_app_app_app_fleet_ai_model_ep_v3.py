"""Fleet AI Model Endpoint v3 — track next-gen model API endpoints."""
from __future__ import annotations
def fleet_ai_model_endpoint_v3(endpoints: list[dict]) -> dict:
    active = [e for e in endpoints if e.get("active", True)]
    total_rps = sum(e.get("rps", 0) for e in endpoints)
    p50 = round(sum(e.get("p50_ms", 0) for e in endpoints) / max(len(endpoints), 1), 1)
    p99 = round(sum(e.get("p99_ms", 0) for e in endpoints) / max(len(endpoints), 1), 1)
    return {"endpoints": len(endpoints), "active": len(active), "rps": total_rps,
            "p50_ms": p50, "p99_ms": p99, "performant": p99 < 100}
