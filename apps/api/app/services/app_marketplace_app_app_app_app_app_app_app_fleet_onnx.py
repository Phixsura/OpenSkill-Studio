"""Fleet ONNX Runtime — track cross-platform ML inference."""
from __future__ import annotations
def fleet_onnx_status(instances: list[dict]) -> dict:
    running = [i for i in instances if i.get("running", True)]
    models = sum(i.get("models", 0) for i in instances)
    inferences_per_sec = sum(i.get("inf_per_sec", 0) for i in instances)
    return {"instances": len(instances), "running": len(running), "models": models,
            "inf_per_sec": inferences_per_sec, "all_running": len(running) == len(instances)}
