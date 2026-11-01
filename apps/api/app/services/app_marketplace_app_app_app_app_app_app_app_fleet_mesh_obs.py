"""Fleet mesh observability — coverage of traces, metrics, logs."""
from __future__ import annotations
def fleet_mesh_observability(services: list[dict]) -> dict:
    with_traces = [s for s in services if s.get("has_traces", False)]
    with_metrics = [s for s in services if s.get("has_metrics", False)]
    with_logs = [s for s in services if s.get("has_structured_logs", False)]
    full = [s for s in services if s.get("has_traces") and s.get("has_metrics") and s.get("has_structured_logs")]
    return {"total": len(services), "with_traces": len(with_traces), "with_metrics": len(with_metrics),
            "with_logs": len(with_logs), "full_observability": len(full),
            "coverage_pct": round(len(full) / max(len(services), 1) * 100, 1)}
