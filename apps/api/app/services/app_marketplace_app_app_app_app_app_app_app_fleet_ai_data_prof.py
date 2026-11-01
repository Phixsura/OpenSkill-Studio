"""Fleet AI Data Profiler — track dataset statistical profiling."""
from __future__ import annotations
def fleet_ai_data_profiler(profilers: list[dict]) -> dict:
    active = [p for p in profilers if p.get("active", True)]
    datasets_profiled = sum(p.get("datasets", 0) for p in profilers)
    columns_analyzed = sum(p.get("columns", 0) for p in profilers)
    anomalies = sum(p.get("anomalies", 0) for p in profilers)
    return {"profilers": len(profilers), "active": len(active), "datasets": datasets_profiled,
            "columns": columns_analyzed, "anomalies": anomalies, "thorough": columns_analyzed > 100}
