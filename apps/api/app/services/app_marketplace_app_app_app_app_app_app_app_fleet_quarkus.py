"""Fleet Quarkus — track supersonic Java framework."""
from __future__ import annotations
def fleet_quarkus_status(services: list[dict]) -> dict:
    running = [s for s in services if s.get("running", True)]
    native_image = [s for s in services if s.get("native", False)]
    startup_ms = round(sum(s.get("startup_ms", 0) for s in services) / max(len(services), 1), 1)
    return {"services": len(services), "running": len(running), "native": len(native_image),
            "avg_startup_ms": startup_ms, "fast": startup_ms < 100}
