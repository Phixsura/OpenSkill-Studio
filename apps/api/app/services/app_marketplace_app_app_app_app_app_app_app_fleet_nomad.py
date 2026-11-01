"""Fleet Nomad — track HashiCorp Nomad job status."""
from __future__ import annotations
def fleet_nomad_status(jobs: list[dict]) -> dict:
    running = [j for j in jobs if j.get("status") == "running"]
    dead = [j for j in jobs if j.get("status") == "dead"]
    pending = [j for j in jobs if j.get("status") == "pending"]
    return {"total": len(jobs), "running": len(running), "dead": len(dead),
            "pending": len(pending), "healthy": len(dead) == 0 and len(pending) == 0}
