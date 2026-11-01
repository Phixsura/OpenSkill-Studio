"""Fleet Ray Serve — track scalable model serving."""
from __future__ import annotations
def fleet_ray_serve(deployments: list[dict]) -> dict:
    running = [d for d in deployments if d.get("status") == "RUNNING"]
    replicas = sum(d.get("replicas", 0) for d in deployments)
    qps = sum(d.get("qps", 0) for d in deployments)
    return {"deployments": len(deployments), "running": len(running), "replicas": replicas,
            "qps": qps, "all_running": len(running) == len(deployments)}
