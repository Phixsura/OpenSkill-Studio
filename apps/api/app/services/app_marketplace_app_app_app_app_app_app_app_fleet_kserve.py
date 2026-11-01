"""Fleet KServe — track Kubernetes ML model serving."""
from __future__ import annotations
def fleet_kserve_status(services: list[dict]) -> dict:
    ready = [s for s in services if s.get("ready", True)]
    models = sum(s.get("models", 0) for s in services)
    qps = sum(s.get("qps", 0) for s in services)
    return {"services": len(services), "ready": len(ready), "models": models,
            "qps": qps, "all_ready": len(ready) == len(services)}
