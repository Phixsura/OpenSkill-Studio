"""Fleet AI Data Privacy — track differential privacy and data protection."""
from __future__ import annotations
def fleet_ai_data_privacy(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    epsilon = round(sum(s.get("epsilon", 0) for s in systems) / max(len(systems), 1), 2)
    datasets_protected = sum(s.get("datasets", 0) for s in systems)
    queries_24h = sum(s.get("queries_24h", 0) for s in systems)
    return {"systems": len(systems), "active": len(active), "epsilon": epsilon,
            "datasets": datasets_protected, "queries_24h": queries_24h, "private": epsilon < 1}
