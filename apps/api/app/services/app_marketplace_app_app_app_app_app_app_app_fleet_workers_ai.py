"""Fleet Workers AI — track edge AI inference."""
from __future__ import annotations
def fleet_workers_ai(models: list[dict]) -> dict:
    active = [m for m in models if m.get("active", True)]
    inferences_24h = sum(m.get("inferences_24h", 0) for m in models)
    avg_latency_ms = round(sum(m.get("avg_latency_ms", 0) for m in models) / max(len(models), 1), 1)
    return {"models": len(models), "active": len(active), "inferences_24h": inferences_24h,
            "avg_latency_ms": avg_latency_ms, "fast": avg_latency_ms < 200}
