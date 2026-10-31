"""Fleet Triton — track NVIDIA inference server."""
from __future__ import annotations
def fleet_triton_status(servers: list[dict]) -> dict:
    ready = [s for s in servers if s.get("ready", True)]
    models_loaded = sum(s.get("models_loaded", 0) for s in servers)
    inferences_per_sec = sum(s.get("inferences_per_sec", 0) for s in servers)
    return {"servers": len(servers), "ready": len(ready), "models_loaded": models_loaded,
            "inferences_per_sec": inferences_per_sec, "all_ready": len(ready) == len(servers)}
