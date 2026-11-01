"""Fleet BentoML — track ML model serving platform."""
from __future__ import annotations
def fleet_bentoml_status(services: list[dict]) -> dict:
    running = [s for s in services if s.get("running", True)]
    bentos = sum(s.get("bentos", 0) for s in services)
    requests_24h = sum(s.get("requests_24h", 0) for s in services)
    return {"services": len(services), "running": len(running), "bentos": bentos,
            "requests_24h": requests_24h, "all_running": len(running) == len(services)}
