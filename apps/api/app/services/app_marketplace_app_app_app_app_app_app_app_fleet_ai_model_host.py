"""Fleet AI Model Hosting — track managed model serving infrastructure."""
from __future__ import annotations
def fleet_ai_model_hosting(hosts: list[dict]) -> dict:
    active = [h for h in hosts if h.get("active", True)]
    models_hosted = sum(h.get("models", 0) for h in hosts)
    endpoints = sum(h.get("endpoints", 0) for h in hosts)
    uptime = round(sum(h.get("uptime_pct", 0) for h in hosts) / max(len(hosts), 1), 3)
    return {"hosts": len(hosts), "active": len(active), "models": models_hosted,
            "endpoints": endpoints, "uptime": uptime, "reliable": uptime > 99.9}
