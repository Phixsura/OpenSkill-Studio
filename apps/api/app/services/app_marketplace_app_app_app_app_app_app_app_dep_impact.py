"""Service dependency impact analyzer — analyze blast radius of service failures."""
from __future__ import annotations
from collections import defaultdict


def analyze_impact(service: str, dependencies: dict[str, list[str]]) -> dict:
    affected = set()
    queue = [service]
    while queue:
        current = queue.pop(0)
        for svc, deps in dependencies.items():
            if current in deps and svc not in affected:
                affected.add(svc)
                queue.append(svc)
    return {"failed_service": service, "affected_services": sorted(affected),
            "blast_radius": len(affected),
            "total_services": len(dependencies),
            "impact_pct": round(len(affected) / max(len(dependencies), 1) * 100, 1)}


def rank_criticality(dependencies: dict[str, list[str]]) -> list[dict]:
    impacts = []
    for svc in set(dep for deps in dependencies.values() for dep in deps) | set(dependencies.keys()):
        result = analyze_impact(svc, dependencies)
        impacts.append({"service": svc, "blast_radius": result["blast_radius"],
                        "impact_pct": result["impact_pct"]})
    return sorted(impacts, key=lambda x: -x["blast_radius"])
