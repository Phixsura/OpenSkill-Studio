"""Fleet Container Runtime v9 — track container runtime security and usage."""
from __future__ import annotations
def fleet_container_runtime_v9(containers: list[dict]) -> dict:
    running = [c for c in containers if c.get("status") == "running"]
    privileged = [c for c in containers if c.get("privileged")]
    cpu_total = sum(c.get("cpu_millicores", 0) for c in containers)
    return {"containers": len(containers), "running": len(running), "privileged": len(privileged),
            "cpu_millicores": cpu_total, "healthy": len(privileged) == 0}
