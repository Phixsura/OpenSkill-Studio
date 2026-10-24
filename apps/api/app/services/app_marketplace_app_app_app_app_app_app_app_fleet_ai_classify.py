"""Fleet AI Classification — track text/image classification."""
from __future__ import annotations
def fleet_ai_classify(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    classifications_24h = sum(s.get("classifications_24h", 0) for s in services)
    accuracy = round(sum(s.get("accuracy_pct", 0) for s in services) / max(len(services), 1), 1)
    return {"services": len(services), "active": len(active), "classifications_24h": classifications_24h,
            "accuracy": accuracy, "high_accuracy": accuracy >= 95}
