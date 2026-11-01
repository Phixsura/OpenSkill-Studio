"""Fleet mesh retry — track retry rates across the mesh."""
from __future__ import annotations
def fleet_mesh_retry(services: list[dict]) -> dict:
    total_req = sum(s.get("requests", 0) for s in services)
    total_retry = sum(s.get("retries", 0) for s in services)
    rate = round(total_retry / max(total_req, 1) * 100, 2)
    return {"requests": total_req, "retries": total_retry, "retry_rate_pct": rate, "excessive": rate > 10}
