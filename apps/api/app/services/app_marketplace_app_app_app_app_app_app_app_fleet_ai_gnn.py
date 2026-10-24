"""Fleet AI Graph Neural Network — track GNN training and inference."""
from __future__ import annotations
def fleet_ai_gnn(models: list[dict]) -> dict:
    active = [m for m in models if m.get("active", True)]
    nodes_processed = sum(m.get("nodes", 0) for m in models)
    edges_processed = sum(m.get("edges", 0) for m in models)
    accuracy = round(sum(m.get("accuracy", 0) for m in models) / max(len(models), 1), 1)
    return {"models": len(models), "active": len(active), "nodes": nodes_processed,
            "edges": edges_processed, "accuracy": accuracy, "effective": accuracy > 85}
