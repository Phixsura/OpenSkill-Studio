"""Fleet AI Model Merging — track model weight averaging and merging."""
from __future__ import annotations
def fleet_ai_model_merge(mergers: list[dict]) -> dict:
    active = [m for m in mergers if m.get("active", True)]
    merges_completed = sum(m.get("merges", 0) for m in mergers)
    methods = set()
    for m in mergers:
        methods.update(m.get("methods", []))
    avg_improvement = round(sum(m.get("improvement_pct", 0) for m in mergers) / max(len(mergers), 1), 1)
    return {"mergers": len(mergers), "active": len(active), "merges": merges_completed,
            "methods": sorted(methods), "improvement": avg_improvement, "effective": avg_improvement > 5}
