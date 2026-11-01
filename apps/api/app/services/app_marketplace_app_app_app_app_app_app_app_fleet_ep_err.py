"""Fleet endpoint error rate — identify noisiest endpoints."""
from __future__ import annotations
def fleet_endpoint_errors(endpoints: list[dict]) -> dict:
    sorted_eps = sorted(endpoints, key=lambda e: e.get("error_rate_pct", 0), reverse=True)
    noisy = [e for e in endpoints if e.get("error_rate_pct", 0) > 5]
    top = sorted_eps[0] if sorted_eps else None
    return {"total": len(endpoints), "noisy_endpoints": len(noisy),
            "worst": top.get("name", "unknown") if top else None,
            "worst_rate": top.get("error_rate_pct", 0) if top else 0}
