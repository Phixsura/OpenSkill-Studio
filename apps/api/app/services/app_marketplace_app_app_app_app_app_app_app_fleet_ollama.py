"""Fleet Ollama — track local LLM runtime."""
from __future__ import annotations
def fleet_ollama_status(instances: list[dict]) -> dict:
    running = [i for i in instances if i.get("running", True)]
    models_loaded = sum(i.get("models_loaded", 0) for i in instances)
    requests_24h = sum(i.get("requests_24h", 0) for i in instances)
    return {"instances": len(instances), "running": len(running), "models_loaded": models_loaded,
            "requests_24h": requests_24h, "all_running": len(running) == len(instances)}
