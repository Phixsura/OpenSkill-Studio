"""Fleet API Dependency v9 — track API inter-dependency graph."""
from __future__ import annotations
def fleet_api_dependency_v9(apis: list[dict]) -> dict:
    with_deps = [a for a in apis if a.get("dependencies")]
    total_deps = sum(len(a.get("dependencies", [])) for a in apis)
    circular = [a for a in apis if a.get("circular_dep")]
    return {"apis": len(apis), "with_deps": len(with_deps), "total_deps": total_deps,
            "circular_deps": len(circular), "healthy": len(circular) == 0}
