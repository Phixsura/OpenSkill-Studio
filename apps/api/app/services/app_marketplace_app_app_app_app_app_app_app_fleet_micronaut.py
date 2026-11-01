"""Fleet Micronaut — track lightweight JVM framework."""
from __future__ import annotations
def fleet_micronaut_status(services: list[dict]) -> dict:
    running = [s for s in services if s.get("running", True)]
    graalvm = [s for s in services if s.get("graalvm", False)]
    memory_mb = round(sum(s.get("memory_mb", 0) for s in services) / max(len(services), 1), 1)
    return {"services": len(services), "running": len(running), "graalvm": len(graalvm),
            "avg_memory_mb": memory_mb, "lightweight": memory_mb < 256}
