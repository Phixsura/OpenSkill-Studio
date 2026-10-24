"""Fleet Cloud Run — track serverless container platform."""
from __future__ import annotations
def fleet_cloudrun_status(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    revisions = sum(s.get("revisions", 0) for s in services)
    requests_24h = sum(s.get("requests_24h", 0) for s in services)
    avg_latency = round(sum(s.get("avg_latency_ms", 0) for s in services) / max(len(services), 1), 1)
    return {"services": len(services), "active": len(active), "revisions": revisions,
            "requests_24h": requests_24h, "avg_latency_ms": avg_latency}
