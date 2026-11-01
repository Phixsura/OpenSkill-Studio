"""Fleet Kubeshark — track API traffic analysis."""
from __future__ import annotations
def fleet_kubeshark_status(captures: list[dict]) -> dict:
    active = [c for c in captures if c.get("active", False)]
    total_requests = sum(c.get("requests_captured", 0) for c in captures)
    anomalies = sum(c.get("anomalies_detected", 0) for c in captures)
    return {"total": len(captures), "active": len(active), "requests_captured": total_requests,
            "anomalies": anomalies, "clean": anomalies == 0}
