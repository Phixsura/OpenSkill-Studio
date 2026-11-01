"""Fleet AI Serving Mesh — track model serving infrastructure."""
from __future__ import annotations
def fleet_ai_serving_mesh(nodes: list[dict]) -> dict:
    healthy = [n for n in nodes if n.get("healthy", True)]
    rps = sum(n.get("rps", 0) for n in nodes)
    p99_ms = max((n.get("p99_ms", 0) for n in nodes), default=0)
    gpu_util = round(sum(n.get("gpu_util", 0) for n in nodes) / max(len(nodes), 1), 1)
    return {"nodes": len(nodes), "healthy": len(healthy), "rps": rps,
            "p99_ms": p99_ms, "gpu_util": gpu_util, "optimal": gpu_util > 70}
