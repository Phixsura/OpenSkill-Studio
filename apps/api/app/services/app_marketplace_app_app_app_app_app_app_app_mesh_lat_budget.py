"""Mesh latency budget — track latency budgets across the mesh."""
from __future__ import annotations
def check_mesh_lat_budget(pairs: list[dict]) -> dict:
    over = [p for p in pairs if p.get("actual_ms", 0) > p.get("budget_ms", 999)]
    return {"total_pairs": len(pairs), "over_budget": len(over),
            "within_budget": len(pairs) - len(over), "all_within": len(over) == 0}
