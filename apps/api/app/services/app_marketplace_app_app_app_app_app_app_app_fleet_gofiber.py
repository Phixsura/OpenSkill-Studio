"""Fleet Go Fiber — track Go web framework health."""
from __future__ import annotations
def fleet_gofiber_status(services: list[dict]) -> dict:
    running = [s for s in services if s.get("running", True)]
    total_rps = sum(s.get("rps", 0) for s in services)
    goroutines = sum(s.get("goroutines", 0) for s in services)
    return {"services": len(services), "running": len(running), "rps": total_rps,
            "goroutines": goroutines, "all_running": len(running) == len(services)}
