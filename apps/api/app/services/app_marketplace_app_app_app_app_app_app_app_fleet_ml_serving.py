"""Fleet ML model serving — track inference latency and throughput."""
from __future__ import annotations
def fleet_ml_serving(models: list[dict]) -> dict:
    total_qps = sum(m.get("qps", 0) for m in models)
    avg_lat = round(sum(m.get("p99_ms", 0) for m in models) / max(len(models), 1), 1)
    stale = [m for m in models if m.get("model_age_days", 0) > 90]
    return {"models": len(models), "total_qps": total_qps, "avg_p99_ms": avg_lat,
            "stale_models": len(stale), "performant": avg_lat < 100}
