"""Fleet Deno Deploy — track edge runtime deployments."""
from __future__ import annotations
def fleet_deno_status(projects: list[dict]) -> dict:
    deployed = [p for p in projects if p.get("deployed", True)]
    total_requests = sum(p.get("requests_24h", 0) for p in projects)
    isolate_time_ms = round(sum(p.get("avg_isolate_ms", 0) for p in projects) / max(len(projects), 1), 1)
    return {"projects": len(projects), "deployed": len(deployed), "requests_24h": total_requests,
            "avg_isolate_ms": isolate_time_ms, "fast": isolate_time_ms < 50}
