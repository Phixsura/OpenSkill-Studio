"""Fleet Vertex AI — track Google ML platform."""
from __future__ import annotations
def fleet_vertex_ai(endpoints: list[dict]) -> dict:
    deployed = [e for e in endpoints if e.get("deployed", True)]
    models = sum(e.get("models", 0) for e in endpoints)
    predictions_24h = sum(e.get("predictions_24h", 0) for e in endpoints)
    return {"endpoints": len(endpoints), "deployed": len(deployed), "models": models,
            "predictions_24h": predictions_24h, "all_deployed": len(deployed) == len(endpoints)}
