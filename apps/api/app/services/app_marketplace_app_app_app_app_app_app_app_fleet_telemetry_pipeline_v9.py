"""Fleet Telemetry Pipeline v9 — track OpenTelemetry collection and export."""
from __future__ import annotations
def fleet_telemetry_pipeline_v9(exporters: list[dict]) -> dict:
    active = [e for e in exporters if e.get("active", True)]
    spans_sec = sum(e.get("spans_per_sec", 0) for e in exporters)
    metrics_sec = sum(e.get("metrics_per_sec", 0) for e in exporters)
    return {"exporters": len(exporters), "active": len(active), "spans_per_sec": spans_sec,
            "metrics_per_sec": metrics_sec, "healthy": len(active) == len(exporters)}
