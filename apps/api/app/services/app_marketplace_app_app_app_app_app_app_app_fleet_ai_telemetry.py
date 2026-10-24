"""Fleet AI Telemetry — track AI system observability and telemetry."""
from __future__ import annotations
def fleet_ai_telemetry(collectors: list[dict]) -> dict:
    active = [c for c in collectors if c.get("active", True)]
    metrics_24h = sum(c.get("metrics_24h", 0) for c in collectors)
    traces_24h = sum(c.get("traces_24h", 0) for c in collectors)
    logs_24h = sum(c.get("logs_24h", 0) for c in collectors)
    return {"collectors": len(collectors), "active": len(active), "metrics_24h": metrics_24h,
            "traces_24h": traces_24h, "logs_24h": logs_24h, "observable": len(active) == len(collectors)}
