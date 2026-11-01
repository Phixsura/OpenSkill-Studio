"""Fleet Zig — track Zig-based service performance."""
from __future__ import annotations
def fleet_zig_status(services: list[dict]) -> dict:
    running = [s for s in services if s.get("running", True)]
    total_rps = sum(s.get("rps", 0) for s in services)
    memory_kb = round(sum(s.get("memory_kb", 0) for s in services) / max(len(services), 1), 1)
    return {"services": len(services), "running": len(running), "rps": total_rps,
            "avg_memory_kb": memory_kb, "ultra_light": memory_kb < 1024}
