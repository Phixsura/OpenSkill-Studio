"""Fleet Spring Boot — track Java microservice framework."""
from __future__ import annotations
def fleet_springboot_status(services: list[dict]) -> dict:
    up = [s for s in services if s.get("status") == "UP"]
    total_beans = sum(s.get("beans", 0) for s in services)
    heap_pct = round(sum(s.get("heap_pct", 0) for s in services) / max(len(services), 1), 1)
    return {"services": len(services), "up": len(up), "beans": total_beans,
            "heap_pct": heap_pct, "all_up": len(up) == len(services)}
