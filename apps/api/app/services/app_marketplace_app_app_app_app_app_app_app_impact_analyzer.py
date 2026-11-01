"""Service dependency impact analyzer — assess blast radius of failures."""
from __future__ import annotations


def analyze_impact(service: str, dependency_graph: dict[str, list[str]]) -> dict:
    affected: set[str] = set()
    queue = [service]
    while queue:
        current = queue.pop(0)
        for svc, deps in dependency_graph.items():
            if current in deps and svc not in affected:
                affected.add(svc)
                queue.append(svc)
    return {"service": service, "affected_services": sorted(affected),
            "blast_radius": len(affected), "total_services": len(dependency_graph),
            "impact_pct": round(len(affected) / max(len(dependency_graph), 1) * 100)}


def risk_ranking(dependency_graph: dict[str, list[str]]) -> list[dict]:
    rankings = []
    for service in dependency_graph:
        impact = analyze_impact(service, dependency_graph)
        rankings.append({"service": service, "blast_radius": impact["blast_radius"],
                          "impact_pct": impact["impact_pct"]})
    return sorted(rankings, key=lambda r: -r["blast_radius"])
