"""Fleet mesh timeout — track timeout rates across the service mesh."""
from __future__ import annotations
def fleet_mesh_timeout(services: list[dict]) -> dict:
    total_req = sum(s.get("requests", 0) for s in services)
    total_timeout = sum(s.get("timeouts", 0) for s in services)
    rate = round(total_timeout / max(total_req, 1) * 100, 2)
    return {"requests": total_req, "timeouts": total_timeout, "timeout_rate_pct": rate, "problematic": rate > 1}
