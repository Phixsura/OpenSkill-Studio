"""Fleet AI Telemetry v3 — track comprehensive platform telemetry."""
from __future__ import annotations
def fleet_ai_telemetry_v3(collectors: list[dict]) -> dict:
    active = [c for c in collectors if c.get("active", True)]
    metrics = sum(c.get("metrics_24h", 0) for c in collectors)
    traces = sum(c.get("traces_24h", 0) for c in collectors)
    logs = sum(c.get("logs_24h", 0) for c in collectors)
    storage_gb = round(sum(c.get("storage_gb", 0) for c in collectors), 1)
    return {"collectors": len(collectors), "active": len(active), "metrics": metrics,
            "traces": traces, "logs": logs, "storage_gb": storage_gb, "comprehensive": metrics > 0 and traces > 0}
