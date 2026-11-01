"""Fleet TorchServe — track PyTorch model serving."""
from __future__ import annotations
def fleet_torchserve_status(instances: list[dict]) -> dict:
    healthy = [i for i in instances if i.get("healthy", True)]
    models = sum(i.get("models", 0) for i in instances)
    predictions_24h = sum(i.get("predictions_24h", 0) for i in instances)
    return {"instances": len(instances), "healthy": len(healthy), "models": models,
            "predictions_24h": predictions_24h, "all_healthy": len(healthy) == len(instances)}
