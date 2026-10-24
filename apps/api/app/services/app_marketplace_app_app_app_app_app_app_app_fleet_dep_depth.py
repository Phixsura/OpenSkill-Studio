"""Fleet dependency depth — track max dependency tree depth."""
from __future__ import annotations
def fleet_dep_depth(services: list[dict]) -> dict:
    depths = [s.get("dep_depth", 0) for s in services]
    max_depth = max(depths) if depths else 0
    avg_depth = round(sum(depths) / max(len(depths), 1), 1)
    deep = [d for d in depths if d > 5]
    return {"services": len(services), "max_depth": max_depth, "avg_depth": avg_depth,
            "too_deep": len(deep), "manageable": max_depth <= 5}
