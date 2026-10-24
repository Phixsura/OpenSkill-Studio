"""Fleet AI Model Pruning — track neural network weight pruning."""
from __future__ import annotations
def fleet_ai_model_pruning(pruners: list[dict]) -> dict:
    active = [p for p in pruners if p.get("active", True)]
    models_pruned = sum(p.get("models", 0) for p in pruners)
    sparsity = round(sum(p.get("sparsity_pct", 0) for p in pruners) / max(len(pruners), 1), 1)
    accuracy_drop = round(sum(p.get("accuracy_drop", 0) for p in pruners) / max(len(pruners), 1), 2)
    return {"pruners": len(pruners), "active": len(active), "models": models_pruned,
            "sparsity": sparsity, "accuracy_drop": accuracy_drop, "lossless": accuracy_drop < 1}
