"""Fleet App Runner — track managed container service."""
from __future__ import annotations
def fleet_apprunner_status(services: list[dict]) -> dict:
    running = [s for s in services if s.get("status") == "RUNNING"]
    instances = sum(s.get("instances", 0) for s in services)
    requests_24h = sum(s.get("requests_24h", 0) for s in services)
    return {"services": len(services), "running": len(running), "instances": instances,
            "requests_24h": requests_24h, "all_running": len(running) == len(services)}
