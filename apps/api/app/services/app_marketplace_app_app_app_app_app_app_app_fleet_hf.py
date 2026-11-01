"""Fleet Hugging Face — track model hub and inference."""
from __future__ import annotations
def fleet_hf_status(spaces: list[dict]) -> dict:
    running = [s for s in spaces if s.get("running", True)]
    models = sum(s.get("models", 0) for s in spaces)
    inferences_24h = sum(s.get("inferences_24h", 0) for s in spaces)
    return {"spaces": len(spaces), "running": len(running), "models": models,
            "inferences_24h": inferences_24h, "all_running": len(running) == len(spaces)}
